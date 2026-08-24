import socket
import ssl

host = "www.python.org"
port = 443

context = ssl.create_default_context()

with socket.create_connection((host, port), timeout=3) as tcp_sock:
    print("tcp=OK")
    print("peer:", tcp_sock.getpeername())

    with context.wrap_socket(tcp_sock, server_hostname=host):
        print("tls=OK")