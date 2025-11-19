import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest

from app.tools.pubmed_client import ingest_pubmed

@pytest.mark.asyncio
async def test_pubmed_ingest():
    count = await ingest_pubmed("lung cancer")
    assert count > 0
