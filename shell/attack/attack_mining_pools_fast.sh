#!/bin/bash
# 快速版本：选择代表性挖矿池域名快速触发检测
for p in minexmr.com xmr.nanopool.org pool.supportxmr.com monero.hashvault.pro xmr.pool.minergate.com monero.herominers.com xmr.2miners.com xmrpool.net supportxmr.com nanopool.org minergate.com moneropool.com monerpool.org linux.monerpool.org xmrpool.eu donate.xmrig.com randomx.xmrig.com nbminer.com herominers.com miningpoolhub.com suprnova.cc dwarfpool.com; do timeout 0.1 host $p >/dev/null 2>&1 || timeout 0.1 curl -s --connect-timeout 0.05 "http://$p" >/dev/null 2>&1; done


