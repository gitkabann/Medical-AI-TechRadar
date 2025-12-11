import pandas as pd
from typing import List, Dict, Any

def generate_comparison_tables(rag_results: List[Any]) -> str:
    if not rag_results:
        return "*(暂无数据生成表格)*"

    # 1. 扁平化
    flat_items = []
    for item in rag_results:
        if isinstance(item, list):
            flat_items.extend(item)
        elif isinstance(item, dict):
            flat_items.append(item)
    
    if not flat_items:
        return "*(暂无有效数据生成表格)*"

    # === 2. 分类提取 + 去重 (Deduplication) ===
    papers = []
    repos = []
    trials = []

    # 用于去重的集合 (记录 url)
    seen_urls = set()

    for item in flat_items:
        if not isinstance(item, dict): continue
        meta = item.get("metadata", {})
        if not meta: continue

        # === 核心修复：去重逻辑 ===
        url = meta.get("url", "#")
        # 如果 URL 有效且已存在，则跳过（避免同一篇论文的多个分块重复显示）
        if url != "#" and url in seen_urls:
            continue
        seen_urls.add(url)
        # ========================

        source = meta.get("source", "").lower()
        title = meta.get("title", "Unknown Title")
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

    # 3. 生成 Markdown (保持不变)
    md_output = []

    if papers:
        df_paper = pd.DataFrame(papers)
        if "Date" in df_paper.columns:
             try: df_paper.sort_values(by="Date", ascending=False, inplace=True)
             except: pass
        md_output.append("### 📄 最新文献对比 (Top Papers)")
        md_output.append(df_paper.to_markdown(index=False))
        md_output.append("\n")

    if repos:
        df_repo = pd.DataFrame(repos)
        md_output.append("### 💻 开源项目概览 (GitHub Repos)")
        md_output.append(df_repo.to_markdown(index=False))
        md_output.append("\n")

    if trials:
        df_trial = pd.DataFrame(trials)
        md_output.append("### 🏥 临床试验进展 (Clinical Trials)")
        md_output.append(df_trial.to_markdown(index=False))
        md_output.append("\n")

    if not md_output:
        return "*(未提取到有效的表格数据)*"

    return "\n".join(md_output)