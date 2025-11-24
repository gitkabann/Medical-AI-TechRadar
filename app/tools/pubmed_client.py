import httpx
from typing import List, Dict
from app.core.logger import get_logger
from app.models.document import DocumentChunk, DocumentMetadata
from app.tools.chunking import chunk_text
import asyncio

def clean_metadata(meta: dict) -> dict:
    """确保 metadata 中所有值都是 Chroma 可接受的类型"""
    safe = {}
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            safe[k] = v
        else:
            safe[k] = str(v)  # datetime、list、dict 全部转字符串
    return safe


logger = get_logger(__name__)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

async def fetch_pubmed(topic: str, retmax: int = 10) -> List[Dict]:
    """搜索 PubMed 并返回论文摘要信息"""
    async with httpx.AsyncClient(timeout=10.0) as client: # AsyncClient 是一个异步 HTTP 会话对象，用来发起 async 的网络请求。
        try:
            # 每次请求前 sleep，避免 PubMed 429
            await asyncio.sleep(0.34)
            
            # Step1: esearch -> 找 PMIDs
            search_resp = await client.get( # 去访问一个网站/接口，返回httpx.Response对象
                f"{BASE_URL}/esearch.fcgi",
                params={"db": "pubmed", 
                        "term": topic, 
                        "retmax": retmax, 
                        "retmode": "json"}
            )
            ids = search_resp.json()["esearchresult"]["idlist"]
            logger.info(f"PubMed 命中 {len(ids)} 条文献")

            if not ids:
                return []
            
            # 第二次请求前再 sleep
            await asyncio.sleep(0.34)

            # Step2: efetch -> 获取摘要等信息
            fetch_resp = await client.get(
                f"{BASE_URL}/efetch.fcgi",
                params={"db": "pubmed", 
                        "id": ",".join(ids), 
                        "retmode": "xml"}
            )

            return parse_pubmed_xml(fetch_resp.text)

        except Exception as e:
            logger.error(f"PubMed 请求失败: {e}")
            return []


def parse_pubmed_xml(xml_text: str) -> List[Dict]:
    """解析 PubMed XML（MVP 简化版）"""
    # 把XML内容解析成字典列表
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_text)

    results = []

    for article in root.findall(".//PubmedArticle"):

        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        abstract = article.findtext(".//AbstractText")
        date = article.findtext(".//PubDate/Year") or ""
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

        if abstract:
            results.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "date": date,
                "url": url,
            })

    return results


async def ingest_pubmed(topic: str):
    """抓取 PubMed → 分块 → 入库"""
    papers = await fetch_pubmed(topic)

    all_chunks: List[DocumentChunk] = []

    for paper in papers:
        meta_raw = {
            "pmid": str(paper["pmid"]),
            "title": str(paper["title"]),
            "date": str(paper["date"]),  # 强制转成字符串
            "url": str(paper["url"]),
        }
        meta_safe = clean_metadata(meta_raw)

        chunks = chunk_text(
            text=paper["abstract"],
            source="pubmed",
            metadata_extra=meta_safe,
        )
        all_chunks.extend(chunks)

    from app.tools.chroma_client import ingest
    ingest(all_chunks)

    return len(all_chunks)