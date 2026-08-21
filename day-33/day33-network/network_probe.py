from urllib.parse import urlparse
import socket
import sys
import http.client
import ssl


if len(sys.argv) != 2:
    print("Kullanim: python network_probe.py <https_url>", file=sys.stderr)
    sys.exit(2)


url = sys.argv[1]

sonuc = urlparse(url)

if sonuc.scheme != "https":
    print("Hata: sadece HTTPS URL kullan", file=sys.stderr)
    sys.exit(1)

if sonuc.hostname is None:
    print("Hata: URL bir hostname icermiyor", file=sys.stderr)
    sys.exit(1)

hostname = sonuc.hostname

try:
    resolved_ip = socket.gethostbyname(hostname)
except socket.gaierror as hata:
    print("Hata meydana geldi:", hata, file=sys.stderr)
    sys.exit(47)
    
path = sonuc.path or "/"

try:
    http_connection = http.client.HTTPSConnection(hostname, port=sonuc.port or 443, timeout=5)
    http_connection.request("GET", path)
    response = http_connection.getresponse()
    status = response.status

except ssl.SSLError as hata:
    print("TLS sırasında hata meydana geldi!", hata, file=sys.stderr)
    sys.exit(74)
    
except TimeoutError as hata:
    print("Timeout hatası meydana geldi!", hata, file=sys.stderr)
    sys.exit(75)
    
except ConnectionError as hata:
    print("Connection sırasında hata meydana geldi!", hata, file=sys.stderr)
    sys.exit(76)
    

print(f"host={hostname}")
print(f"resolved_ip={resolved_ip}")
print(f"status={status}")