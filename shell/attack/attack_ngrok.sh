#!/bin/bash
# 模拟攻击：连接ngrok域名 - 触发EDR检测规则

# ngrok域名后缀（从规则中提取）
DOMAINS=(
    "test-12345.ngrok-free.app"
    "malicious.ngrok-free.dev"
    "c2-server.ngrok.app"
    "exfil.ngrok.dev"
    "backdoor.ngrok.io"
    "evil-123.ngrok-free.app"
    "payload.ngrok-free.dev"
    "tunnel-abc.ngrok.app"
    "data-exfil.ngrok.dev"
    "c2-tunnel.ngrok.io"
)

# 快速批量连接所有ngrok域名
for domain in "${DOMAINS[@]}"; do
    # 方法1: 使用curl (HTTP/HTTPS)
    timeout 0.5 curl -s --connect-timeout 0.3 "http://$domain" >/dev/null 2>&1 || \
    timeout 0.5 curl -s --connect-timeout 0.3 "https://$domain" >/dev/null 2>&1
    
    # 方法2: 使用wget
    timeout 0.5 wget --spider --timeout=0.3 "http://$domain" 2>/dev/null || \
    timeout 0.5 wget --spider --timeout=0.3 "https://$domain" 2>/dev/null
    
    # 方法3: 使用nc (TCP连接)
    timeout 0.5 nc -zv "$domain" 80 2>&1 | head -1 >/dev/null 2>&1 || \
    timeout 0.5 nc -zv "$domain" 443 2>&1 | head -1 >/dev/null 2>&1
done


