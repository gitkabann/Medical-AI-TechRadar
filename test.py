import httpx
print(httpx.get("https://ipinfo.io/ip").text)
import requests

url = "https://clinicaltrials.gov/api/v2/studies"
resp = requests.get(
    url,
    params={"query.term": "rectal cancer", "pageSize": 5},
    headers={"User-Agent": "Mozilla/5.0"}  # 防止403
)

data = resp.json()

for study in data.get("studies", []):
    title = study["protocolSection"]["identificationModule"].get("briefTitle")
    print(title)