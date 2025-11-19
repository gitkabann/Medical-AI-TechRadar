import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest

from app.tools.github_client import search_repos, fetch_readme, ingest_github

@pytest.mark.asyncio
async def test_search_repos():
    repos = await search_repos("medical imaging", limit=2)
    print("search_repos result:", repos)   # <-- 调试输出
    assert len(repos) == 2
    assert "full_name" in repos[0]
    assert "stars" in repos[0]


@pytest.mark.asyncio
async def test_fetch_readme():
    # 使用一个稳定的仓库
    readme = await fetch_readme("torvalds/linux")
    print("fetch_readme result length:", len(readme))  # <-- 内容长度
    print("fetch_readme preview:", readme[:200])       # <-- 前200字
    assert isinstance(readme, str)
    assert len(readme) > 0


@pytest.mark.asyncio
async def test_ingest_github():
    """测试 GitHub 数据是否成功进入 Chroma."""
    from app.tools.chroma_client import client

    before = client.get_or_create_collection("medical_docs").count()
    print("before ingest:", before)  # <-- 调试输出

    n_chunks = await ingest_github("cancer imaging", top_n=1)
    print("number of chunks ingested:", n_chunks)  # <-- 调试输出
    after = client.get_or_create_collection("medical_docs").count()
    print("after ingest:", after)  # <-- 调试输出
    assert n_chunks > 0
    assert after > before
