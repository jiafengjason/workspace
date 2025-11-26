#!/bin/bash
# 超高效版本：使用DNS查询快速触发（最快方法）
for d in test-12345.ngrok-free.app malicious.ngrok-free.dev c2-server.ngrok.app exfil.ngrok.dev backdoor.ngrok.io; do host $d >/dev/null 2>&1 || curl -s --connect-timeout 0.1 "http://$d" >/dev/null 2>&1; done


