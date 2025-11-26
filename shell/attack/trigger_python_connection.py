#!/usr/bin/env python3
# 模拟攻击：Python进程发起网络连接 - 触发EDR检测规则
# 用于测试 net_connection_win_python.yml

import socket
import sys
import time

# 目标服务器（使用外部IP，确保不是本地127.0.0.1）
TARGETS = [
    ("8.8.8.8", 53),      # Google DNS
    ("1.1.1.1", 53),      # Cloudflare DNS
    ("208.67.222.222", 53),  # OpenDNS
    ("8.8.4.4", 53),      # Google DNS备用
]

print("Python网络连接测试 - 触发EDR检测规则")
print("=" * 50)

# 方法1: 使用socket连接
for host, port in TARGETS:
    try:
        print(f"[测试] 连接到 {host}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        print(f"  连接尝试完成")
        time.sleep(0.2)
    except Exception as e:
        print(f"  错误: {e}")
        time.sleep(0.2)

# 方法2: HTTP连接（使用urllib）
try:
    import urllib.request
    print("\n[测试] HTTP连接测试")
    urllib.request.urlopen("http://8.8.8.8", timeout=1)
except:
    pass

# 方法3: HTTPS连接
try:
    import urllib.request
    print("[测试] HTTPS连接测试")
    urllib.request.urlopen("https://1.1.1.1", timeout=1)
except:
    pass

print("\n测试完成！请检查EDR系统日志。")


