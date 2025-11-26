#!/usr/bin/env python3
# 简化版：快速触发Python网络连接检测
import socket
for h,p in [("8.8.8.8",53),("1.1.1.1",53),("208.67.222.222",53)]:
    s=socket.socket();s.settimeout(0.5);s.connect_ex((h,p));s.close()


