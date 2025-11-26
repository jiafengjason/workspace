#!/bin/bash
# 模拟恶意软件后门连接攻击 - 快速触发 EDR 检测

TARGET="8.8.8.8"
PORTS=(4444 8080 8888 5552 777 666 1443 1515 1777 1817 1904 1960 2443 2448 3360 3675 3939 4040 4433 4438 4443 4455 5445 5649 6625 7210 8143 8843 9631 9943 10101 12102 12103 12322 13145 13394 13504 13505 13506 13507 14102 14103 14154 49180 65520 65535)

# 快速批量连接所有可疑端口
if command -v nc &>/dev/null; then
    for p in "${PORTS[@]}"; do timeout 0.3 nc -zv "$TARGET" "$p" 2>&1; done
else
    for p in "${PORTS[@]}"; do timeout 0.3 bash -c "echo >/dev/tcp/$TARGET/$p" 2>/dev/null; done
fi

