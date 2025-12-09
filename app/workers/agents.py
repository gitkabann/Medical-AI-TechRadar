# app/workers/agents.py
import asyncio
from app.core.base_worker import BaseWorker
from app.core.event_bus import bus, Topic
from app.models.protocol import TaskPayload
from app.tools.pubmed_client import ingest_pubmed
from app.tools.arxiv_client import ingest_arxiv
from app.tools.github_client import ingest_github
from app.tools.trials_client import ingest_trials
from app.tools.rag_query import query_rag
from app.agents.writer import generate_markdown_report
from app.tools.pdf_exporter import save_markdown_as_pdf
from app.core.state_manager import state_manager
from app.core.memory import task_memory

# 1. Planner Agent: 选择和决定任务的下一个 Agent。（目前是透传）
class PlannerAgent(BaseWorker):
    def __init__(self):
        super().__init__(Topic.PLANNER, Topic.CRAWLER)

    def process(self, payload: TaskPayload) -> TaskPayload:
        # 这里未来做 Planning，现在直接透传
        topic = payload.topic
        print(f"🧠 [Planner] 规划任务: {topic}")
        # 初始化任务记录
        state_manager.init_task(payload.task_id, payload.topic, payload.params)

        # === 记忆检索 =============
        # 尝试回忆是否做过类似任务
        past_knowledge = task_memory.recall_task(topic)
        if past_knowledge:
            print(f"[Planner] 发现类似任务记忆: {past_knowledge['topic']}")
            print("[Planner] 策略调整: 跳过抓取，复用历史知识。")
            # 将历史数据注入 Payload
            payload.data["rag_context"] = [{
                "content": f"【历史知识复用】\n之前的研究总结：{past_knowledge['summary']}",
                "metadata": {"source": "Memory", "type": "history"}
            }]
            # 直接发布到 Writer
            next_payload = payload.next_step("memory_hit")
            bus.publish(Topic.WRITER, next_payload.model_dump())
            return None # 阻止后续流程
        # ===========================
        return payload.next_step("crawling_started")

# 2. Crawler Agent: 负责并发抓取
class CrawlerAgent(BaseWorker):
    def __init__(self):
        super().__init__(Topic.CRAWLER, Topic.RAG)

    def process(self, payload: TaskPayload) -> TaskPayload:
        topic = payload.topic
        print(f"🕷️ [Crawler] 开始多源抓取: {topic}")

        async def run_crawlers():
            # 并发执行
            results = await asyncio.gather(
                ingest_pubmed(topic),
                ingest_arxiv(topic),
                ingest_github(topic, top_n=1),
                return_exceptions=True 
            )
            # 解析结果，统计成功/失败
            sources = ["PubMed", "ArXiv", "GitHub"]
            status_report = {}
            
            for source, res in zip(sources, results):
                if isinstance(res, Exception):
                    print(f"⚠️ [Crawler] {source} 抓取失败: {res}")
                    status_report[source] = "Failed"
                else:
                    print(f"✅ [Crawler] {source} 抓取成功，数量: {res}")
                    status_report[source] = "Success"

            # 处理 Trials (同步函数，单独包 try-except)
            try:
                ingest_trials(topic)
                status_report["Trials"] = "Success"
            except Exception as e:
                print(f"⚠️ [Crawler] Trials 抓取失败: {e}")
                status_report["Trials"] = "Failed"

            return status_report
        
        # 运行爬虫
        status = asyncio.run(run_crawlers())
        # 只要不是全部失败，就认为是部分成功
        # 将抓取状态传递给下游
        return payload.next_step("crawling_done", {"crawl_status": status})

# 3. RAG Agent: 负责检索
class RagAgent(BaseWorker):
    def __init__(self):
        super().__init__(Topic.RAG, Topic.WRITER)

    def process(self, payload: TaskPayload) -> TaskPayload:
        topic = payload.topic
        print(f"🔍 [RAG] 正在检索上下文...")
        
        results = query_rag(topic, top_k=5)
        # 将结果存入 data 传递给 Writer
        # 注意：results 是 dict 列表，可以直接序列化
        
        return payload.next_step("rag_done", {"rag_context": results})

# 4. Writer Agent: 生成报告
class WriterAgent(BaseWorker):
    def __init__(self):
        super().__init__(Topic.WRITER, None) # 链条终点，不再发布

    def process(self, payload: TaskPayload) -> TaskPayload:
        topic = payload.topic
        context = payload.data.get("rag_context", [])
        
        print(f"✍️ [Writer] 正在撰写报告...")
        report = generate_markdown_report(topic, context)
        
        # 保存文件
        task_id = payload.task_id
        md_path = f"report_{task_id}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report)
            
        # 导出 PDF
        try:
            pdf_path = save_markdown_as_pdf(task_id, report)
            print(f"🎉 [Writer] 任务完成！PDF: {pdf_path}")
        except Exception:
            print("⚠️ PDF 生成失败，但 MD 已保存")

        # === 存入记忆 ===
        # 提取报告的前 500 字作为摘要存入记忆库
        summary = report[:500].replace("#", "").replace("*", "")
        task_memory.remember_task(
            topic=topic,
            summary=summary,
            artifact_path=pdf_path
        )
        print(f"🧠 [Writer] 已将本任务存入长期记忆库。")
        # ==============================
        return None # 结束