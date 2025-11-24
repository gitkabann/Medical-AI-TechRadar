import asyncio
from app.tools.pubmed_client import ingest_pubmed
from app.tools.arxiv_client import ingest_arxiv
from app.tools.github_client import ingest_github
from app.tools.chroma_client import ingest
from app.tools.rag_query import query_rag
from app.agents.writer import generate_markdown_report

async def run_pipeline(topic: str):
    print(f"=== [1] 拉取 PubMed: {topic} ===")
    await ingest_pubmed(topic)

    print(f"=== [2] 拉取 arXiv ===")
    await ingest_arxiv(topic)

    print(f"=== [3] 拉取 GitHub ===")
    await ingest_github(topic, top_n=1)

    print(f"=== [4] 查询 RAG ===")
    rag_results = query_rag(topic, top_k=5)

    print(f"=== [5] 生成报告 ===")
    report = generate_markdown_report(topic, rag_results)

    with open("demo_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("🎉 已生成 demo_report.md")
    print("=== 报告内容 ===")
    print(report)
    return report

if __name__ == "__main__":
    asyncio.run(run_pipeline("polyp segmentation"))