from urllib.parse import urlparse
import argparse
import http.client
import sys


parser = argparse.ArgumentParser()
parser.add_argument("url")
args = parser.parse_args()

url = urlparse(args.url)

if url.scheme != "http":
    print("Hata: sadece http:// destekleniyor", file=sys.stderr)
    sys.exit(1)

if url.hostname is None:
    print("Hata: URL hostname içermiyor", file=sys.stderr)
    sys.exit(1)

host = url.hostname
port = url.port or 80

path = url.path or "/"

if url.query:
    target = path + "?" + url.query
else:
    target = path

try:
    connection = http.client.HTTPConnection(host, port, timeout=3)

    connection.request("GET", target)
    response = connection.getresponse()

    body = response.read()

    print(f"url={args.url}")
    print(f"status={response.status}")
    print(f"body_bytes={len(body)}")
    print(f"body_preview={body.decode(errors='replace')[:100]}")

    connection.close()

except (OSError, http.client.HTTPException) as hata:
    print(f"HTTP bağlantı hatası: {hata}", file=sys.stderr)
    sys.exit(1)