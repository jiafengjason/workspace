import socket
import sys

def udp_client(message, host='172.31.0.1', port=12345):
    try:
        socket.inet_pton(socket.AF_INET6, host)
        family = socket.AF_INET6
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET, host)
            family = socket.AF_INET
        except socket.error:
            print("Invalid IP address format!")
            return

    sock = socket.socket(family, socket.SOCK_DGRAM)
    
    try:
        server_address = (host, int(port))
        print("send to %s" % host)
        sent = sock.sendto(message.encode(), server_address)
        
        data, server = sock.recvfrom(1024)
        print("from server: %s get: %s" % (server, data.decode()))
        
    finally:
        print("close")
        sock.close()

if __name__ == "__main__":
    test_message = "aaaaaaaaaaaaaaaaaaaaaaa"
    host = sys.argv[1]
    port = sys.argv[2]
    udp_client(test_message, host, port)
