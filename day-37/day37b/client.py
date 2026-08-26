from urllib.request import urlopen

url = "http://api:8000"

with urlopen(url, timeout=3) as response:
	body = response.read().decode("utf-8")

print("status:", response.status)
print("body:", body)
