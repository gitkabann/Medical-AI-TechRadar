# app\agents\run_pipeline.py
import asyncio
from uuid import uuid4
from app.tools.pubmed_client import ingest_pubmed
from app.tools.arxiv_client import ingest_arxiv
from app.tools.github_client import ingest_github
from app.tools.trials_client import ingest_trials
from app.tools.rag_query import query_rag
from app.agents.writer import generate_markdown_report
from app.tools.pdf_exporter import save_markdown_as_pdf  # 确保这里用的是新写的带 weasyprint 的版本
from app.core.metrics import tracker

async def run_pipeline(topic: str):
    # 生成一个任务 ID
    task_id = str(uuid4())
    print(f"任务 ID: {task_id}")

    # 开始总计时
    tracker.start_pipeline()
    try:
        # 1. PubMed
        print(f"=== [1] 拉取 PubMed: {topic} ===")
        with tracker.track("pubmed"):
            await ingest_pubmed(topic)

        # 2. arXiv (即使报错，metrics 也会记录 fail)
        print(f"=== [2] 拉取 arXiv ===")
        try:
            with tracker.track("arxiv"):
                await ingest_arxiv(topic)
        except Exception as e:
            print(f"⚠️ arXiv 步骤异常 (已记录): {e}")

        # 3. GitHub
        print(f"=== [3] 拉取 GitHub ===")
        with tracker.track("github"):
            await ingest_github(topic, top_n=1)

        # 4. ClinicalTrials
        print(f"=== [4] 拉取 ClinicalTrials ===")
        with tracker.track("trials"):
            # 如果 trials 还是同步函数，直接调；如果是 async 就加 await
            ingest_trials(topic)

        # 5. RAG Query
        print(f"=== [5] 查询 RAG ===")
        rag_results = None
        with tracker.track("rag_query"):
            rag_results = query_rag(topic, top_k=5)

        # 6. Report Generation
        print(f"=== [6] 生成报告 ===")
        report = ""
        with tracker.track("writer"):
            report = generate_markdown_report(topic, rag_results)
            # 保存 MD
            with open(f"demo_report_{task_id}.md", "w", encoding="utf-8") as f:
                f.write(report)

        # 7. PDF Export
        print("=== [7] 导出 PDF ===")
        try:
            with tracker.track("export_pdf"):
                save_markdown_as_pdf(task_id, report)
        except Exception as e:
            print(f"⚠️ PDF 导出跳过: {e}")

    finally:
        # 无论成功失败，最后打印指标表
        tracker.report()

    return report

if __name__ == "__main__":
    asyncio.run(run_pipeline("polyp segmentation"))