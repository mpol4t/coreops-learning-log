import json
from urllib.request import Request, urlopen

url = "http://127.0.0.1:18081/assets"

request = Request(
    url,
    headers={
        "Accept": "application/json",
        "Authorization": "Bearer coreops-demo-token",
    },
)

with urlopen(request, timeout=3) as response:
    body = response.read().decode("utf-8")
    data = json.loads(body)

print("status:", response.status)
print("data:", data)
print(response.headers.get("Content-Type"))