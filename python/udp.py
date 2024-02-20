import socket

def send(udp_socket):
    """创建从键盘接收的信息"""
    msg = input("\n请输入要发送的数据:")
    """键盘输入ip"""
    destip = input("\n请输入对应的ip:")
    """键盘输入port"""
    destport = int(input("\n请输入对应的port:"))
    """发送数据"""
    udp_socket.sendto(msg.encode("utf-8"), (destip, destport))

def recv(udp_socket):
    """接收数据"""
    recv_data = udp_socket.recvfrom(1024)
    """解码数据"""
    recvip = recv_data[1]
    recvmsg = recv_data[0].decode("gbk")
    """格式化打印数据"""
    print("%s:%s", (str(recvip), recvmsg))

def main():
    """创建套接字"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    """对端口号进行绑定"""
    udp_socket.bind(("", 7878))
    """循环实现相应的功能"""

    while True:

        print("-" * 30)
        print("1:发送信息")
        print("2:接收信息")
        print("exit:关闭运行")
        print("-" * 30)

        op_num = input("请输入相应的功能模块：")
        if op_num == "1":
            send(udp_socket)
        elif op_num == "2":
            recv(udp_socket)
        elif op_num == "exit":
            break
        else:
            print("输入错误,请重新输入")

if __name__ == '__main__':
    main()
