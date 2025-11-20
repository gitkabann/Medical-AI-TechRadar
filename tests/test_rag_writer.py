import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.agents.pipeline_dummy import run_pipeline

def test_rag_writer():
    md = run_pipeline("肺结节分割")
    assert "关键文献总结" in md
    assert "引用" in md
    print(md)
