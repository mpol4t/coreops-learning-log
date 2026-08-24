from urllib.parse import urlparse
import argparse
import socket
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("url")
args = parser.parse_args()

url = urlparse(args.url)

if url.scheme != "https" and url.scheme != "http":
    print("Hata: unsupported scheme", file=sys.stderr)
    sys.exit(1)

if url.hostname is None:
    print("Hata: URL bir hostname içermiyor", file=sys.stderr)
    sys.exit(1)

host = url.hostname
port = url.port
path = url.path or "/"
query = url.query

if port is None:
    if url.scheme == "https":
        port = 443
    elif url.scheme == "http":
        port = 80

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
        connected_peer_port = peer[1]
        peer_in_candidates = connected_peer_ip in ips

        print("Host:", host)
        print("Port:", port)
        print("DNS candidates:",ips)
        print("Peer ip:",connected_peer_ip)
        print("Peer port:", connected_peer_port)
        print("Peer in candidates:",peer_in_candidates)
        print("TCP: OK")
        time.sleep(10)
        
except socket.error as hata:
    print("TCP bağlantı hatası:", hata, file=sys.stderr)
    sys.exit(1)