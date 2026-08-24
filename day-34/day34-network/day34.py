from urllib.parse import urlparse
import argparse
import socket
import sys


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

        print(f"host={host}")
        print(f"port={port}")
        print(f"dns_candidates={sorted(ips)}")
        print(f"connected_peer_ip={connected_peer_ip}")
        print(f"connected_peer_port={connected_peer_port}")
        print(f"peer_in_candidates={peer_in_candidates}")
        print("tcp=OK")
except OSError as hata:
    print("TCP bağlantı hatası:", hata, file=sys.stderr)
    sys.exit(1)