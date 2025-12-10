import pandas as pd
from typing import List, Dict, Any

def generate_comparison_tables(rag_results: List[Any]) -> str:
    """
    输入：RAG 检索到的 chunks (可能包含嵌套列表)
    输出：Markdown 表格
    """
    if not rag_results:
        return "*(暂无数据生成表格)*"

    # === 1. 数据扁平化 (Flatten) ===
    # 解决输入是 [[], [{...}, {...}]] 这种嵌套结构的问题
    flat_items = []
    for item in rag_results:
        if isinstance(item, list):
            flat_items.extend(item)  # 如果是列表，拆包并追加
        elif isinstance(item, dict):
            flat_items.append(item)  # 如果是字典，直接追加
    
    # 如果扁平化后没数据
    if not flat_items:
        return "*(暂无有效数据生成表格)*"
    # ==============================

    # === 2. 数据分类与提取 ===
    papers = []
    repos = []
    trials = []

    for item in flat_items:
        # 双重保险：确保 item 是字典
        if not isinstance(item, dict):
            continue

        meta = item.get("metadata", {})
        if not meta:
            continue

        source = meta.get("source", "").lower()
        title = meta.get("title", "Unknown Title")
        url = meta.get("url", "#")
        date = meta.get("date", "N/A")

        if "github" in source:
            repos.append({
                "Project": f"[{title}]({url})",
                "Date": date,
                "Stars": meta.get("stars", "N/A"),
                "Language": meta.get("language", "N/A")
            })
        elif "trial" in source or "clinical" in source:
            trials.append({
                "Trial Title": f"[{title}]({url})",
                "Status": meta.get("status", "Unknown"),
                "Phase": meta.get("phase", "N/A"),
                "Location": meta.get("location", "N/A")[:20] + "..."
            })
        else:
            # 默认为文献
            papers.append({
                "Paper Title": f"[{title}]({url})",
                "Source": source.capitalize(),
                "Date": date,
                "DOI": meta.get("doi", "N/A")
            })

    # === 3. 生成 Markdown 表格 ===
    md_output = []

    # 文献表
    if papers:
        df_paper = pd.DataFrame(papers)
        if "Date" in df_paper.columns:
             try:
                df_paper.sort_values(by="Date", ascending=False, inplace=True)
             except: pass
        md_output.append("### 📄 最新文献对比 (Top Papers)")
        md_output.append(df_paper.to_markdown(index=False))
        md_output.append("\n")

    # GitHub 表
    if repos:
        df_repo = pd.DataFrame(repos)
        md_output.append("### 💻 开源项目概览 (GitHub Repos)")
        md_output.append(df_repo.to_markdown(index=False))
        md_output.append("\n")

    # Trial 表
    if trials:
        df_trial = pd.DataFrame(trials)
        md_output.append("### 🏥 临床试验进展 (Clinical Trials)")
        md_output.append(df_trial.to_markdown(index=False))
        md_output.append("\n")

    if not md_output:
        return "*(未提取到有效的表格数据)*"

    return "\n".join(md_output)