# app/agents/writer.py
from app.agents.fact_enricher import (
    extract_key_facts,
    classify_facts,
    enrich_with_trials,
)


def generate_markdown_report(topic: str, rag_bundle):
    """
    综合 writer：生成结构化医学技术报告（Markdown）
    rag_bundle = (trial_chunks, other_chunks)
    """

    trial_chunks, other_chunks = rag_bundle

    md = []
    # 1. 标题
    md.append(f"# 医学技术自动化报告：{topic}\n")

    # 2. 摘要（Summary）
    md.append("## 摘要\n")
    md.append(
        f"本报告通过 PubMed、arXiv、GitHub 以及 ClinicalTrials.gov 等多个公开数据源，"
        f"自动收集与分析了 **{topic}** 相关的研究证据、技术趋势及结构化试验结果，"
        f"并对多来源证据进行一致性比对，以提升医学证据的可解释性。\n"
    )

    # 3. 对比要点（Highlights）
    md.append("\n## 对比要点（Highlights）\n")
    md.append(
        "- **PubMed**：医学文献数量与研究热点趋势\n"
        "- **arXiv**：最新前沿研究方向\n"
        "- **GitHub**：技术实现成熟度、代码活跃度\n"
        "- **ClinicalTrials**：真实世界结构化临床试验证据\n"
    )

    # 4. ClinicalTrials 结构化增强（Trial Enrich）
    trial_section = enrich_with_trials(trial_chunks)
    if trial_section:
        md.append("\n## 临床试验概览（ClinicalTrials）\n")
        md.append(trial_section)

    # 5. RAG 检索主要结果摘要
    md.append("\n## 文献/技术检索要点（RAG Summary）\n")

    if not other_chunks:
        md.append("暂无文献或技术类检索结果。\n")
    else:
        for c in other_chunks[:3]:
            source = c["metadata"].get("source", "?")
            md.append(f"- **{source}**: {c['content'][:180]}...\n")

    # 6. 事实抽取 + 多来源一致性（Fact Enricher）
    fact_map = extract_key_facts(trial_chunks + other_chunks)
    conclusion, to_verify = classify_facts(fact_map)

    md.append("\n## 结论区（多来源一致的事实）\n")
    if not conclusion:
        md.append("暂无一致结论。\n")
    else:
        for item in conclusion:
            md.append(f"- {item['fact']} （来源数：{len(item['support'])}）\n")

    md.append("\n## 待核实区（证据不足）\n")
    if not to_verify:
        md.append("暂无。\n")
    else:
        for item in to_verify:
            md.append(f"- {item['fact']} （来源数：{len(item['support'])}）\n")

    # 7. 附录：ClinicalTrials 明细列表
    md.append("\n## 附录：ClinicalTrials 试验列表\n")
    if not trial_chunks:
        md.append("暂无临床试验记录。\n")
    else:
        for t in trial_chunks[:5]:
            meta = t["metadata"]
            md.append(
                f"- **{meta.get('trial_title', '无标题')}**  "
                f"（状态：{meta.get('trial_status', '未知')}，地点：{meta.get('location', '未知')}）\n"
            )

    # 8. 引用（References）
    md.append("\n## 引用（References）\n")
    for i, item in enumerate(trial_chunks + other_chunks, start=1):
        url = item["metadata"].get("url", "#")
        source = item["metadata"].get("source", "unknown")
        md.append(f"[{i}] **{source}** → {url}\n")

    # 输出 Markdown 字符串
    return "\n".join(md)
