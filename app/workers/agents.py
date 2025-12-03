import asyncio
from app.core.base_worker import BaseWorker
from app.core.event_bus import Topic
from app.models.protocol import TaskPayload
from app.tools.pubmed_client import ingest_pubmed
from app.tools.arxiv_client import ingest_arxiv
from app.tools.github_client import ingest_github
from app.tools.trials_client import ingest_trials
from app.tools.rag_query import query_rag
from app.agents.writer import generate_markdown_report
from app.tools.pdf_exporter import save_markdown_as_pdf
from app.core.state_manager import state_manager

# 1. Planner Agent: 选择和决定任务的下一个 Agent。（目前是透传）
class PlannerAgent(BaseWorker):
    def __init__(self):
        super().__init__(Topic.PLANNER, Topic.CRAWLER)

    def process(self, payload: TaskPayload) -> TaskPayload:
        # 这里未来做 Planning，现在直接透传
        print(f"🧠 [Planner] 规划任务: {payload.topic}")
        # 初始化任务记录
        state_manager.init_task(payload.task_id, payload.topic, payload.params)
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
            await asyncio.gather(
                ingest_pubmed(topic),
                ingest_arxiv(topic),
                ingest_github(topic, top_n=1)
            )
            # ingest_trials 目前是同步的
            ingest_trials(topic)

        # 在同步方法中运行异步代码
        asyncio.run(run_crawlers())
        
        return payload.next_step("crawling_done", {"crawl_status": "success"})

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

        return None # 结束