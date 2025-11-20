def generate_markdown_report(topic: str, rag_results: list[dict]) -> str:
    """根据 RAG 结果生成 Markdown 报告（3段落 + 引用）"""

    # 提取引用
    refs = []
    for i, r in enumerate(rag_results[:3]):
        meta = r["metadata"]
        url = meta.get("url", "#")
        source = meta.get("source", "unknown")
        refs.append(f"{i+1}. **{source}** — [{meta.get('title', 'Untitled')}]({url})")

    # 拼报告
    md = f"""
# {topic} 技术雷达 - 自动摘要报告

## 一、关键文献总结
基于向量检索，系统从 PubMed 与 arXiv 中找到多篇与你主题相关的技术论文。这些论文涵盖最新算法、模型架构、实验结果，体现了当前研究重点方向。

## 二、代码实现趋势
从 GitHub 代码仓库来看，社区近期更新较为活跃，包含若干深度学习实现、训练脚本、评估工具。其中部分仓库提供了开箱即用的 pipeline，为你的模型研发提供重要参考。

## 三、临床试验进展
根据 ClinicalTrials.gov 的结构化数据，相关试验显示研究方向正在向更大规模验证、更多中心合作靠拢，体现了该任务的临床价值逐渐提高。

## 🔗 引用
{chr(10).join(refs)}
"""
    return md.strip()
