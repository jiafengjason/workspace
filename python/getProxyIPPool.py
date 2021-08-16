#coding=utf-8
import requests
import re
import time
import csv

proxyHost = "192.168.105.108"
proxyPort = "9910"
print(proxyHost,proxyPort)

proxyMeta = "http://%(host)s:%(port)s" % {
    "host" : proxyHost,
    "port" : proxyPort,
}
proxies = {
    "http"  : proxyMeta,
    "https"  : proxyMeta
}
headers = {
   'Connection': 'keep-alive',
   'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
   'sec-ch-ua-mobile': '?0',
   'Upgrade-Insecure-Requests': '1',
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
   'Sec-Fetch-Site': 'same-origin',
   'Sec-Fetch-Mode': 'navigate',
   'Sec-Fetch-User': '?1',
   'Sec-Fetch-Dest': 'document',
   'Referer': 'https://www.kuaidaili.com/free/inha/1/',
   'Accept-Language': 'zh-CN,zh;q=0.9',
}

for page in range(1,50):
    print(page)
    response = requests.get(f'https://www.kuaidaili.com/free/inha/{page}/', headers=headers, proxies=proxies)
    ip_list = re.findall('data-title="IP">(.*?)</td>',response.text)
    print(ip_list)
    time.sleep(1)
    
pool = []
for ip in ip_list:
   try:
       response = requests.get('https://www.baidu.com', proxies=ip, timeout=2)
       if response.status_code == 200:
           pool.append(ip)
   except:
       print(ip, '检测不通过')
   else:
       print(ip, '检测通过')
print(pool)

with open('ip.csv','a',newline='') as f:
   writer = csv.writer(f)
   writer.writerow(pool)