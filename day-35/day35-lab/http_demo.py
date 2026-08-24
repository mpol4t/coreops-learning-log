from urllib.request import urlopen

url = "http://127.0.0.1:18080/"

with urlopen(url, timeout=3) as response:
    status = response.status
    body = response.read().decode("utf-8")

print("status:", status)
print("body:", body)