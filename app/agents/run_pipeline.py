import asyncio
from uuid import uuid4
from app.tools.pubmed_client import ingest_pubmed
from app.tools.arxiv_client import ingest_arxiv
from app.tools.github_client import ingest_github
from app.tools.trials_client import ingest_trials
from app.tools.rag_query import query_rag
from app.agents.writer import generate_markdown_report
from app.tools.pdf_exporter import save_markdown_as_pdf  # 确保这里用的是新写的带 weasyprint 的版本

async def run_pipeline(topic: str):
    # 生成一个任务 ID
    task_id = str(uuid4())
    print(f"任务 ID: {task_id}")

    print(f"=== [1] 拉取 PubMed: {topic} ===")
    await ingest_pubmed(topic)

    print(f"=== [2] 拉取 arXiv ===")
    await ingest_arxiv(topic)

    print(f"=== [3] 拉取 GitHub ===")
    await ingest_github(topic, top_n=1)

    print(f"=== [4] 拉取 ClinicalTrials ===")
    ingest_trials(topic)

    print(f"=== [5] 查询 RAG ===")
    rag_results = query_rag(topic, top_k=5)

    print(f"=== [6] 生成报告 ===")
    report = generate_markdown_report(topic, rag_results)

    # 保存 MD
    md_filename = f"app/artifacts/demo_report_{task_id}.md"
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"已生成 Markdown: {md_filename}")

    # 保存 PDF
    print("=== [7] 导出 PDF ===")
    # 传入 task_id 和 报告内容
    pdf_path = save_markdown_as_pdf(task_id, report)
    print(f"已生成 PDF: {pdf_path}")

    return report

if __name__ == "__main__":
    asyncio.run(run_pipeline("polyp segmentation"))