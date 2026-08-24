from urllib.parse import urlparse
import argparse
import socket
import ssl
import sys


parser = argparse.ArgumentParser()
parser.add_argument("url")
args = parser.parse_args()

url = urlparse(args.url)

if url.scheme != "https":
    print("Hata: sadece https:// destekleniyor", file=sys.stderr)
    sys.exit(1)

if url.hostname is None:
    print("Hata: URL bir hostname içermiyor", file=sys.stderr)
    sys.exit(1)

host = url.hostname
port = url.port
path = url.path or "/"
query = url.query

if port is None:
    port = 443

try:
    results = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
except socket.gaierror as hata:
    print("DNS hatası meydana geldi:", hata, file=sys.stderr)
    sys.exit(1)

ips = set()

for item in results:
    family, socktype, proto, canonname, sockaddr = item
    ips.add(sockaddr[0])

try:
    with socket.create_connection((host, port), timeout=3) as sock:
        peer = sock.getpeername()
        connected_peer_ip = peer[0]

        print("Host:", host)
        print("Port:", port)
        print("Peer ip:",connected_peer_ip)
        print("TCP: OK")
        
        context = ssl.create_default_context()
        try:
            with context.wrap_socket(sock, server_hostname=host):
                print("TLS: Ok")
        except ssl.SSLError as hata:
            print("TLS bağlantısı hatası:", hata, file=sys.stderr)
            sys.exit(1)
            
except socket.error as hata:
    print("TCP bağlantı hatası:", hata, file=sys.stderr)
    sys.exit(1)
    
