import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.tools.trials_client import ingest_trials
import httpx

print(httpx.get("https://ipinfo.io/ip").text)
def test_ingest_trials():
    count = ingest_trials("lung cancer")
    assert count > 0