import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import asyncio
from app.agents.pipeline_dummy import ingest_all_sources

def test_async_pipeline():
    topic = "cancer"
    results = asyncio.run(ingest_all_sources(topic))

    pubmed, arxiv, github, trials = results

    assert isinstance(pubmed, int)
    assert isinstance(arxiv, int)
    assert isinstance(github, int)
    assert isinstance(trials, int)
