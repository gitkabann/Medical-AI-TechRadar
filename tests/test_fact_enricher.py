import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.agents.fact_enricher import extract_key_facts, classify_facts

def test_fact_enricher_basic():
    mock = [
        {"content": "A 是正确的。A 有研究支持。", 
        "metadata": {"source": "pubmed", "url": "..."}},
        {"content": "A 是正确的。B 需要更多研究。", 
        "metadata": {"source": "arxiv", "url": "..."}},
    ]

    fact_map = extract_key_facts(mock)
    conclusion, to_verify = classify_facts(fact_map)

    assert len(conclusion) >= 1   # A 被两个来源支持
