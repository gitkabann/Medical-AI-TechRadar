from typing import Dict, Any

def is_valid_url(url: str) -> bool:
    return isinstance(url, str) and url.startswith(("http://", "https://"))

def clean_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
    """修复 metadata：空字段、非法字段、URL 修复"""
    meta = meta.copy()

    # 1. 去掉 None / 空值
    for k, v in list(meta.items()):
        if v in (None, "", [], {}):
            meta[k] = "unknown"

    # 2. URL 修复
    if "url" in meta and not is_valid_url(meta["url"]):
        meta["url"] = "unknown"

    return meta


def is_valid_chunk(content: str) -> bool:
    """过滤空摘要、无内容、只有符号的 chunk"""
    if not isinstance(content, str):
        return False
    text = content.strip()
    if len(text) < 20:  # 太短的 chunk 无意义
        return False
    return True