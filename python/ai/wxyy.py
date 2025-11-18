import requests
import json

# 替换为你的API Key和Secret Key
API_KEY = 'PFHgwKKhJ0MAwGlSsMnILTfD'
SECRET_KEY = 'KhJR4NMiNouXkZUKt0EzCootf9xBgRC9'

# 获取access_token的函数
def get_access_token():
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
    response = requests.post(url)
    return response.json().get("access_token")

# 调用文心一言API的函数
def call_wenxin_api(message, access_token):
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 1.0,
        "response_format": "json_object"
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload)
    return response.json()

# 获取access_token
access_token = get_access_token()
print("Access Token:", access_token)

# 调用文心一言API并打印结果
result = call_wenxin_api("你好，文心一言！", access_token)
print("API调用结果:", result)
