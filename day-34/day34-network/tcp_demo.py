import socket

host = "example.com"
port = 80

with socket.create_connection((host, port), timeout=3) as sock:
    peer = sock.getpeername()

    print("connected_peer:", peer)