from socket import *

def to_ascii(h):
    list_s = []
    for i in range(0,len(h),2):
        list_s.append(chr(int(h[i:i+2],16)))
    return ''.join(list_s)

udp_socket = socket(type=SOCK_DGRAM)
udp_socket.bind(('',2425))

udp_socket.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
#data = '1:1648630053:DESKTOP-1234567:DESKTOP-1234567:1:DESKTOP-1234567 WorkGroup E4-54-E8-A1-EA-AB      192.168.101.25  8 10000001  DESKTOP-1234567'
data = '313a313634383633313236393a4445534b544f502d313233343536373a4445534b544f502d313233343536373a333a4445534b544f502d3132333435363700576f726b47726f75700045342d35342d45382d43432d34362d45350000000000003139322e3136382e3130312e36320000323000313030303030303100004445534b544f502d31323334353637'

fqdata = to_ascii(data)
print(fqdata)

address=('192.168.101.62',2425)
udp_socket.sendto(fqdata.encode('gbk'),address)
udp_socket.close()
