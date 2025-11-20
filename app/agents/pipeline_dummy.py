import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.agents.writer import generate_markdown_report

from app.core.logger import get_logger
from app.tools.rag_query import query_rag
from app.agents.writer import generate_markdown_report

logger = get_logger(__name__)

def plan(topic: str) -> dict:
    """Day5 简易计划器（代替真实 Agent）"""
    logger.info("开始规划任务步骤...")
    return {
        "steps": [
            "搜索相关文献",
            "搜索相关代码库",
            "检查相关临床试验",
            "生成 Markdown 报告"
        ]
    }

def query_dummy_rag(topic: str) -> list[dict]:
    """RAG 的伪数据；Day5 只需要假数据跑通流程"""
    logger.info("执行假数据 RAG 检索…")

    return [
        {
            "source": "PubMed",
            "text": f"{topic} 在 2024 年有显著研究进展……"
        },
        {
            "source": "GitHub",
            "text": f"相关代码库已在 {topic} 任务中获得应用……"
        },
        {
            "source": "ClinicalTrials",
            "text": f"{topic} 相关的临床试验正在进行中……"
        },
    ]

def run_pipeline(topic: str) -> str:
    logger.info(f"开始最小流水线执行（MVP）：{topic}")

    # 1. 生成计划
    plan_result = plan(topic)
    logger.info(f"计划生成完成：{plan_result['steps']}")

    # 2. RAG 检索
    results = query_rag(topic, top_k=5)
    logger.info(f"RAG 检索返回 {len(results)} 条内容")

    # 3. 生成 MD 报告
    md = generate_markdown_report(topic, results)
    logger.info("Markdown 报告生成完成")

    return md


if __name__ == "__main__":
    topic = "息肉检测"
    md = run_pipeline(topic)

    print("\n===== 最终输出（Markdown） =====\n")
    print(md)