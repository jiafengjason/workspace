import os
import quandl

# 设置代理服务器的地址和端口
proxy_address = "http://192.168.74.10:9910"
 
# 设置环境变量
os.environ['HTTP_PROXY'] = proxy_address
os.environ['HTTPS_PROXY'] = proxy_address

quandl.ApiConfig.api_key = "9Ys_anKS8a2E-GnoWArF"
data = quandl.get("WIKI/AAPL", rows=5)
print(data)

