from app.tools.dummy_search import DummySearchTool
from app.tools.schema import SearchOutput
def test_dummy_search():
    tool = DummySearchTool()
    result = tool.run({"query": "肺结节分割"})
    assert isinstance(result, SearchOutput)
    assert isinstance(result.results, list)
    assert len(result.results) > 0
