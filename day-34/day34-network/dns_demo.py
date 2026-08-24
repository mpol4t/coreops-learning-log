import socket

host = "example.com"
port = 443

results = socket.getaddrinfo(host, port)

ips = set()
for item in results:
    family, socktype, proto, canonname, sockaddr = item
    
    ips.add(sockaddr[0])
    
for x in ips:
    print(x)