def generate_markdown_report(topic: str, findings: list[dict]) -> str:
    """最小 Writer：把 RAG 的伪数据写成 Markdown 报告"""
    md = f"# {topic} 调研报告\n\n"

    for item in findings:
        source = item.get("source", "Unknown")
        text = item.get("text", "")
        md += f"### 来源：{source}\n{text}\n\n"

    md += "---\n_本报告为最小占位版本（Pipeline MVP），内容为伪数据。_"
    return md