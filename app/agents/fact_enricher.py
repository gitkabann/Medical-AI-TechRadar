# app/agents/fact_enricher.py
import re
from typing import List, Dict, Any

def extract_key_facts(rag_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    把每条检索到的 RAG 片段的文本按句子拆开。
    """
    fact_map = {}

    for item in rag_results:
        content = item.get("content", "")
        if not content:
            continue
            
        # === 修复：使用正则同时支持中文句号(。)和英文句号(.) ===
        # 解释：按 . 或 。 或 ! ? 分割，并去除空白
        # 英文句号后通常有空格，所以 split(". ") 也是一种简单策略，这里用正则更稳
        sentences = re.split(r'[.。!！?？]', content)
        
        # 清洗
        clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 10] # 长度阈值稍微调高到10，过滤无意义短语
        # ====================================================

        for s in clean_sentences:
            if s not in fact_map: 
                fact_map[s] = []
            fact_map[s].append(item)
            
    return fact_map

def classify_facts(fact_map: Dict[str, List[Dict[str, Any]]]):
    """
    v1 一致性策略：
      - >=2 个不同来源 source 支持 → 结论区
      - 否则 → 待核实区
    """
    conclusion = []
    to_verify = []

    for fact, items in fact_map.items():
        # 统计来源数量
        sources = {item["metadata"].get("source", "unknown") for item in items}

        if len(sources) >= 2:
            conclusion.append({"fact": fact, "support": items})
        else:
            to_verify.append({"fact": fact, "support": items})
    
    # 按来源数降序排序，让证据多的排前面
    conclusion.sort(key=lambda x: len(x["support"]), reverse=True)
    to_verify.sort(key=lambda x: len(x["support"]), reverse=True)

    return conclusion, to_verify

def enrich_with_trials(trial_items: List[Dict[str, Any]]) -> str:
    # ... (这部分保持不变)
    if not trial_items:
        return ""

    lines = ["### 结构化临床试验证据（优先使用）\n"]

    for item in trial_items:
        meta = item.get("metadata", {}) # 加个安全get
        lines.append(
            f"- **{meta.get('trial_title', 'unknown')}** | 状态: {meta.get('trial_status', 'N/A')} "
            f"| 样本量: {meta.get('trial_enrollment', 'N/A')} | 阶段: {meta.get('trial_phase', 'N/A')} "
            f"([链接]({meta.get('url', '#')}))"
        )

    return "\n".join(lines)