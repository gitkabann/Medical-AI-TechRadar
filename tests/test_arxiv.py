import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
import asyncio
from app.tools.arxiv_client import ingest_arxiv

@pytest.mark.asyncio
async def test_arxiv_ingest():
    count = await ingest_arxiv("cancer")
    assert count > 0
