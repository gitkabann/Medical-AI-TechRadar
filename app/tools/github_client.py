import httpx
import base64
from typing import List, Dict
from app.core.logger import get_logger
from app.tools.chunking import chunk_text
from app.models.document import DocumentChunk
from app.core.config import settings

logger = get_logger(__name__)

GITHUB_API = "https://api.github.com"


def _auth_headers():
    """如果你在 .env 设置了 GITHUB_TOKEN，这里会启用认证，避免频繁限流。"""
    if hasattr(settings, "github_token") and settings.github_token:
        return {"Authorization": f"Bearer {settings.github_token}"}
    return {}


async def search_repos(keyword: str, limit: int = 10) -> List[Dict]:
    """
    用 GitHub 的搜索 API 搜项目：按关键词 + Star 数排序。
    """
    url = f"{GITHUB_API}/search/repositories"
    params = {
        "q": keyword,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params, headers=_auth_headers())
        resp.raise_for_status()#HTTP 响应状态码不是成功（非 2xx），就主动抛出异常
        data = resp.json()

    repos = []
    for repo in data.get("items", []):
        repos.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "updated_at": repo["updated_at"],
        })

    logger.info(f"[GitHub] 状态码：{resp.status_code}，找到 {len(repos)} 个仓库（keyword='{keyword}'）")
    return repos


async def fetch_readme(full_name: str) -> str:
    """
    获取 README（base64 编码，需要解码）
    """
    url = f"{GITHUB_API}/repos/{full_name}/readme"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=_auth_headers())
        # print("fetch_readme status:", resp.status_code)     # 调试
        # print("fetch_readme headers:", resp.headers)        # 调试
        # print("fetch_readme text preview:", resp.text[:200])# 调试
        if resp.status_code != 200:
            return ""
        data = resp.json()

    content = data.get("content", "")
    if not content:
        print("content empty")
        return ""
    
    try:
        decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
        return decoded
    except Exception as e:
        print("decode error:", e)
        return ""


async def fetch_latest_release(full_name: str) -> str:
    """
    获取最近 Release（可能没有）
    """
    url = f"{GITHUB_API}/repos/{full_name}/releases/latest"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=_auth_headers())
        if resp.status_code != 200:
            return ""
        data = resp.json()

    body = data.get("body", "")
    return body or ""


async def fetch_commit_frequency(full_name: str, weeks: int = 12) -> int:
    """
    用 GitHub API 统计最近 X 周 commit 数。
    """
    url = f"{GITHUB_API}/repos/{full_name}/stats/commit_activity"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=_auth_headers())
        if resp.status_code != 200:
            return 0
        data = resp.json()

    # 最近 N 周的 commit 总数
    return sum(week["total"] for week in data[-weeks:])


def clean_text(text: str, max_len: int = 5000) -> str:
    """简单清洗：去掉过长文本、去空行、多余空格"""
    if not text:
        return ""

    text = text.strip()

    # 过长文本直接截断
    if len(text) > max_len:
        text = text[:max_len] + "\n...\n[TRUNCATED]"

    return text


async def ingest_github(keyword: str, top_n: int = 5) -> int:
    """
    GitHub → 分块 → 入库
    """
    repos = await search_repos(keyword, limit=top_n)
    all_chunks: List[DocumentChunk] = []

    from app.tools.chroma_client import ingest

    for repo in repos:
        full = repo["full_name"]

        readme = await fetch_readme(full)
        release = await fetch_latest_release(full)
        commits = await fetch_commit_frequency(full)

        summary_text = (
            f"# Repo: {full}\n"
            f"Stars: {repo['stars']}\n"
            f"Updated at: {repo['updated_at']}\n"
            f"Commit Frequency (12 weeks): {commits}\n\n"
        )

        combined_text = summary_text + "\n## README\n" + readme + "\n\n## Release Notes\n" + release
        combined_text = clean_text(combined_text)
        chunks = chunk_text(
            text=combined_text,
            source="github",
            metadata_extra={
                "repo": full,
                "url": repo["url"],
                "stars": repo["stars"],
                "updated_at": repo["updated_at"],
            }
        )

        all_chunks.extend(chunks)

    ingest(all_chunks)
    return len(all_chunks)