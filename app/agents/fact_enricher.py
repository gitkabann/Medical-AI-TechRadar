from typing import List, Dict, Any

# rag_item: {"content": str, "metadata": dict, "score": float}

def extract_key_facts(rag_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    把每条检索到的 RAG 片段的文本按句子拆开作为“事实”，并记录每个事实由哪些检索片段支持。（MVP：句子切分）
    返回：
      { fact_str: [支持该事实的 rag_result_items] }
    """
    fact_map = {}

    for item in rag_results:
        content = item["content"]
        sentences = [s.strip() for s in content.split("。") if len(s.strip()) > 3] #按 句号 切分句子，并做简单清洗
        
        #将每个句子切分，如果有相同的短语出现，就合并到字典的同一个 key 对应的列表中，作为一个“事实”
        for s in sentences:
            if s not in fact_map: #如果这个句子还没作为 key 出现过
                fact_map[s] = [] #就先建一个空列表
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
        sources = {item["metadata"].get("source", "") for item in items}

        if len(sources) >= 2:
            conclusion.append({"fact": fact, "support": items})
        else:
            to_verify.append({"fact": fact, "support": items})

    return conclusion, to_verify


def enrich_with_trials(trial_items: List[Dict[str, Any]]) -> str:
    """
    将 trial 的结构化信息拼成 markdown 段落，优先作为提示词证据。
    """
    if not trial_items:
        return ""

    lines = ["### 结构化临床试验证据（优先使用）\n"]

    for item in trial_items:
        meta = item["metadata"]
        lines.append(
            f"- **{meta.get('trial_title', 'unknown')}** | 状态: {meta.get('trial_status')} "
            f"| 样本量: {meta.get('trial_enrollment')} | 阶段: {meta.get('trial_phase')} "
            f"([链接]({meta.get('url', '#')}))"
        )

    return "\n".join(lines)