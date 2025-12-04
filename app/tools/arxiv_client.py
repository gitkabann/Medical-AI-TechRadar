import httpx
from typing import List, Dict
from app.core.logger import get_logger
from app.tools.chunking import chunk_text
from app.models.document import DocumentChunk
from app.core.chaos import chaos  # 导入混沌

logger = get_logger(__name__)

async def fetch_arxiv(topic: str, max_results: int = 10) -> List[Dict]:
    # === 埋雷 ===
    try:
        chaos.simulate("ArXiv_API") 
    except ConnectionError as e:
        print(f"⚠️ {e}")
        raise e 
    # ============
    """
    搜索 arXiv 文献，返回 title/abstract/date/url/doi 等信息。
    arXiv 使用 Atom XML，需要手动解析。
    """
    try:
        ARXIV_API = "https://export.arxiv.org/api/query"
        headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Agentic-RAG/1.0; +https://example.com)"
        }
        # 构造查询 URL
        params = {
            "search_query": f"all:{topic}",
            "start": 0,
            "max_results": max_results,
        }

        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(ARXIV_API, params=params)
            print(f"📡 [ArXiv] HTTP 状态码: {resp.status_code}")
            if resp.status_code != 200:
                print(f"❌ ArXiv 返回错误状态码。内容摘要: {resp.text[:200]}")
                return []
            xml_text = resp.text

            papers = parse_arxiv_xml(xml_text)
            logger.info(f"[arXiv] 状态码：{resp.status_code}，解析到 {len(papers)} 篇论文（topic='{topic}'）")

            return papers
            
    except Exception as e:
        logger.error(f"ArXiv 请求失败: {e}")
        return []


def parse_arxiv_xml(xml_text: str) -> List[Dict]:
    """
    解析 arXiv API 返回的 Atom XML。
    """
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    results = []

    for entry in root.findall("atom:entry", ns):

        title = entry.find("atom:title", ns).text or ""
        print("Title:", title)
        abstract = entry.find("atom:summary", ns).text or ""

        date = entry.find("atom:published", ns).text or ""

        url = entry.find("atom:id", ns).text or ""

        # DOI 是可选的
        doi_node = entry.find(".//atom:doi", ns)
        doi = doi_node.text if doi_node is not None else None

        results.append({
            "title": title.strip(),
            "abstract": abstract.strip(),
            "date": date,
            "url": url,
            "doi": doi,
        })

    return results


async def ingest_arxiv(topic: str) -> int:
    """arXiv → 分块 → 入库"""
    papers = await fetch_arxiv(topic)
    all_chunks: List[DocumentChunk] = []

    for paper in papers:
        chunks = chunk_text(
            text=paper["abstract"],
            source="arxiv",
            metadata_extra=paper,
        )
        all_chunks.extend(chunks)

    from app.tools.chroma_client import ingest
    ingest(all_chunks)

    return len(all_chunks)
