import argparse
import base64
import hashlib
import hmac
import os
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import random
import socket
import sys

# 派生密钥和 IV 的函数
def derive_key_and_iv(password, salt):
    # 第一次 MD5: MD5(pwd + salt)
    md5_1 = hashlib.md5(password + salt).digest()
    # 第二次 MD5: MD5(md5_1 + pwd + salt)
    md5_2 = hashlib.md5(md5_1 + password + salt).digest()
    # 256位密钥 = md5_1 + md5_2
    key = md5_1 + md5_2
    # IV = MD5(md5_2 + pwd + salt)（取前16字节）
    iv_full = hashlib.md5(md5_2 + password + salt).digest()
    iv = iv_full[:16]  # 取前16字节作为IV
    return key, iv

def gen_spa_message(args):
    # 生成随机字符串（16位数字）
    rand_val = ''.join(str(random.randint(0, 9)) for _ in range(16))
    print(rand_val)

    # 获取时间戳（秒）
    timestamp = int(time.time())
    message = "192.168.112.142,tcp/58679,tcp/443"
    version = "4.0.0"
    inner_id = "enlink"
    outer_id = "enlink"

    # Base64 编码消息（去除填充的=）
    encoded_msg = base64.b64encode(message.encode('latin-1')).decode('utf-8')
    encoded_msg = encoded_msg.strip('=')

    # 构建编码消息字符串
    encoded_msg_str = f"{rand_val}:cm9vdA:{timestamp}:{version}:{args.deviceid}:7:{encoded_msg}"
    print(encoded_msg_str)

    # 计算 SHA256 哈希
    encoded_msg_sha256 = hashlib.sha256(encoded_msg_str.encode('utf-8')).digest()
    encoded_msg_sha256_b64 = base64.b64encode(encoded_msg_sha256).decode('utf-8')
    encoded_msg_sha256_b64 = encoded_msg_sha256_b64.strip('=')
    print("sha256 result", encoded_msg_sha256_b64)

    # 构建数据字符串
    data = f"{encoded_msg_str}:{encoded_msg_sha256_b64}:{inner_id}"
    print("data", data)

    # 生成密钥（MD5("Enlink@123")）
    enkey = hashlib.md5("Enlink@123".encode('utf-8')).digest()

    # 生成随机 salt（8字节）
    salt = os.urandom(8)
    # salt = bytes.fromhex("ea12274e694fbc43")  # 如果需要固定 salt

    key, iv = derive_key_and_iv(enkey, salt)
    print(key.hex(), iv.hex())

    # 使用 AES-CBC 加密数据
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 数据需要填充到16字节的倍数
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_data)

    # 构建加密结果（Salted__ + salt + encrypted）
    salted_prefix = b"Salted__" + salt
    encrypted_b64 = base64.b64encode(salted_prefix + encrypted).decode('utf-8')
    encrypted_b64 = encrypted_b64.strip('=')
    print("result", encrypted_b64)
    
    # 计算 HMAC-MD5
    hmac_msg = hmac.new(enkey, encrypted_b64.encode('utf-8'), hashlib.md5).digest()
    hmac_msg_b64 = base64.b64encode(hmac_msg).decode('utf-8')
    hmac_msg_b64 = hmac_msg_b64.strip('=')
    print("hmac result", hmac_msg_b64)

    # 构建最终数据（去掉加密结果的前10个字符 + HMAC + outer_id）
    final_data = encrypted_b64[10:] + hmac_msg_b64 + outer_id
    print("data", final_data)
    return final_data

def udp_client(message, args):
    try:
        socket.inet_pton(socket.AF_INET6, args.server)
        family = socket.AF_INET6
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET, args.server)
            family = socket.AF_INET
        except socket.error:
            print("Invalid IP address format!")
            return

    sock = socket.socket(family, socket.SOCK_DGRAM)
    
    try:
        server_address = (args.server, args.port)
        print(f"send to {args.server}")
        sent = sock.sendto(message.encode(), server_address)
        
    finally:
        print("close")
        sock.close()

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--server",
        type=str,
        default="192.168.114.139",
        help="Server host"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=62201,
        help="Server port"
    )
    parser.add_argument(
        "-d", "--deviceid",
        type=str,
        default="69EC299FD51DF3334D82F9D43A9C41B1",
        help="Device id"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v: INFO, -vv: DEBUG)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = setup_args()
    message = gen_spa_message(args)
    udp_client(message, args)