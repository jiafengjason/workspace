#coding=utf-8
import requests
import sys

targetUrl = "https://www.baidu.com"
proxyHost = sys.argv[1]
proxyPort = sys.argv[2]
print(proxyHost,proxyPort)

proxyMeta = "http://%(host)s:%(port)s" % {
    "host" : proxyHost,
    "port" : proxyPort,
}
print(proxyMeta)
#pip install -U requests[socks]  socks5 
# proxyMeta = "socks5://%(host)s:%(port)s" % {
#     "host" : proxyHost,
#     "port" : proxyPort,
# }

proxies = {
    "http"  : proxyMeta,
    "https"  : proxyMeta
}
resp = requests.get(targetUrl, proxies=proxies, timeout=2)
if resp.status_code == 200:
   print(proxyHost,proxyPort, '检测通过')