import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import asyncio
from app.agents.writer import generate_markdown_report
from app.core.logger import get_logger
from app.tools.rag_query import query_rag
from app.tools.pubmed_client import ingest_pubmed
from app.tools.arxiv_client import ingest_arxiv
from app.tools.github_client import ingest_github
from app.tools.trials_client import ingest_trials
from app.core.async_utils import with_retry
from app.core.config import settings

logger = get_logger(__name__)

async def ingest_trials_safe(topic: str):
    """
    trials.gov 必须同步调用 → 用 asyncio.to_thread 包一下
    """
    return await asyncio.to_thread(ingest_trials, topic)

async def ingest_all_sources(topic: str):
    """
    PubMed / arXiv / GitHub 并发
    Trials.gov 单独顺序执行
    """
    tasks = [
        with_retry(ingest_pubmed, topic),
        with_retry(ingest_arxiv, topic),
        with_retry(ingest_github, topic),
    ]
    pubmed, arxiv, github = await asyncio.gather(*tasks)
    trials = await ingest_trials_safe(topic)

    return pubmed, arxiv, github, trials


async def run_pipeline(topic: str):
    logger.info(f"开始最小流水线执行（MVP）：{topic}")

    # 并发获取数据
    pubmed, arxiv, github, trials = await ingest_all_sources(topic)
    logger.info("ingest_all_sources 执行完成")

    return {
        "topic": topic,
        "pubmed": pubmed,
        "arxiv": arxiv,
        "github": github,
        "trials": trials,
    }



if __name__ == "__main__":
    topic = "息肉检测"
    md = run_pipeline(topic)

    print("\n===== 最终输出（Markdown） =====\n")
    print(md)