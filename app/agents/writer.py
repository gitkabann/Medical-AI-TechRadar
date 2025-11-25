from app.agents.fact_enricher import extract_key_facts, classify_facts, enrich_with_trials

def generate_markdown_report(topic: str, rag_bundle):
    trial_chunks, other_chunks = rag_bundle   # 解包你的 rag_query 返回结果

    trial_section = enrich_with_trials(trial_chunks)

    # 事实抽取 + 一致性判断
    fact_map = extract_key_facts(trial_chunks + other_chunks)
    conclusion, to_verify = classify_facts(fact_map)

    md = [f"# 关于「{topic}」的自动报告\n"]

    if trial_section:
        md.append(trial_section)

    md.append("\n\n## 结论区（多来源一致）\n")
    if not conclusion:
        md.append("暂无一致结论。\n")
    else:
        for c in conclusion:
            md.append(f"- {c['fact']} （来源数：{len(c['support'])}）\n")

    md.append("\n\n## 待核实区（证据不足）\n")
    if not to_verify:
        md.append("暂无。\n")
    else:
        for c in to_verify:
            md.append(f"- {c['fact']} （来源数：{len(c['support'])}）\n")

    md.append("\n\n## 引用\n")
    for item in trial_chunks + other_chunks:
        url = item["metadata"].get("url", "#")
        md.append(f"- [{item['metadata']['source']}]({url})\n")

    return "\n".join(md)