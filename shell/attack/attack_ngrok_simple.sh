#!/bin/bash
# 模拟攻击：快速触发ngrok域名检测（单行命令）
for d in test-12345.ngrok-free.app malicious.ngrok-free.dev c2-server.ngrok.app exfil.ngrok.dev backdoor.ngrok.io evil-123.ngrok-free.app payload.ngrok-free.dev tunnel-abc.ngrok.app data-exfil.ngrok.dev c2-tunnel.ngrok.io; do timeout 0.2 curl -s "http://$d" >/dev/null 2>&1 || timeout 0.2 curl -s "https://$d" >/dev/null 2>&1 || timeout 0.2 host $d >/dev/null 2>&1 || timeout 0.2 nc -zv $d 80 2>&1 >/dev/null; done

