from urllib.parse import urlparse

url = "https://example.com:8443/data"

parts = urlparse(url)
port = parts.port

if port is None:
    if parts.scheme == "https":
        port = 443
    elif parts.scheme == "http":
        port = 80
        
print("Port:", port)