import socket

def udp_server(host='::', port=12345):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    
    sock.bind((host, port))
    
    print("Start %s:%s" % (host, port))
    
    while True:
        data, addr = sock.recvfrom(1024)
        print "from %s get: %s" % (addr, data)
        
        response = "get: %s" % data
        sock.sendto(response, addr)

if __name__ == "__main__":
    udp_server()
