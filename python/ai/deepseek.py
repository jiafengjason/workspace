import requests

# API Key 和请求 URL
api_key = 'sk-4b5f2a482b424108b8e62efec9a68fa0'
url = 'https://api.deepseek.com/search'

# 设置请求头和参数
headers = {
    'Authorization': f'Bearer {api_key}'
}
params = {
    'query': 'your_search_keyword'
}

# 发起请求
response = requests.get(url, headers=headers, params=params)

# 检查响应状态码和内容
if response.status_code == 200:
    print('API Key 有效')
    data = response.json()
    # 处理响应数据...
else:
    print(f'API Key 可能无效，响应状态码：{response.status_code}')
    print(response.text)
