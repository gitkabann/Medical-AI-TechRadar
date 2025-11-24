import requests
from typing import List, Dict, Any
from app.models.document import DocumentChunk
from app.core.data_clean import clean_metadata
from app.tools.chunking import chunk_text

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_trials(topic: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """同步请求 ClinicalTrials.gov"""
    params = {
        "query.term": topic,
        "pageSize": max_results,
    }

    resp = requests.get(
        BASE_URL,
        params=params,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )

    resp.raise_for_status()
    return resp.json().get("studies", [])


def parse_trial_metadata(trial: Dict[str, Any]) -> Dict[str, Any]:
    """解析 ClinicalTrials 字段，带 trial_* 命名空间"""

    protocol = trial["protocolSection"]
    ident = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})

    meta = {
        "trial_id": ident.get("nctId"),
        "trial_title": ident.get("briefTitle"),
        "trial_status": status.get("overallStatus"),
        "trial_enrollment": design.get("enrollmentInfo", {}).get("count"),
        "url": f"https://clinicaltrials.gov/study/{ident.get('nctId')}",
    }

    return clean_metadata(meta)


def trial_to_chunk(trial: Dict[str, Any]) -> List[DocumentChunk]:
    """把一个 trial 转成 DocumentChunk"""

    protocol = trial["protocolSection"]
    ident = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})

    text = f"""
Trial Title: {ident.get('briefTitle')}
Status: {status.get('overallStatus')}
Enrollment: {design.get('enrollmentInfo', {}).get('count')}
"""

    meta = parse_trial_metadata(trial)

    chunks = chunk_text(
        text=text,
        source="clinical_trials",
        metadata_extra=meta,
    )

    return chunks


def ingest_trials(topic: str, max_results: int = 5) -> int:
    """ClinicalTrials.gov → 分块 → 入库"""
    from app.tools.chroma_client import ingest

    trials = fetch_trials(topic, max_results=max_results)

    all_chunks = []
    for t in trials:
        chunks = trial_to_chunk(t)
        all_chunks.extend(chunks)

    ingest(all_chunks)
    return len(all_chunks)