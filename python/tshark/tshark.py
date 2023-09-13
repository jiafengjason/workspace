import pyshark

# 加载本地的pcap文件
capture = pyshark.FileCapture('8000.pcap')

# 遍历所有的数据包
for packet in capture:
    # 获取数据包的源IP地址
    src_ip = packet.ip.src
    # 获取数据包的目的IP地址
    dst_ip = packet.ip.dst
    # 获取数据包的协议
    protocol = packet.transport_layer
    # 输出数据包的信息
    print(f"Packet: {protocol} from {src_ip} to {dst_ip}")

# 捕获本机的网络流量
capture = pyshark.LiveCapture(interface='ens192')

# 获取所有的捕获数据包
for packet in capture.sniff_continuously():
    # 输出每个数据包的协议信息
    print(packet.highest_layer)
    # 输出每个数据包的IP地址信息
    if 'IP' in packet:
        print(packet.ip)