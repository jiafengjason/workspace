import requests

ip = "114.221.154.43"
ak = "f6XFTs5afvi6EXaGhgFCRpIYmo0UcG9E"

url = "http://api.map.baidu.com/location/ip"
params = {"ip": ip, "ak": ak, "coor": "bd09ll"}
response = requests.get(url, params=params)
result = response.json()

if result["status"] == 0:
    #{'address': 'CN|江苏省|南京市|None|None|100|100', 'content': {'address': '江苏省南京市', 'address_detail': {'adcode': '320100', 'city': '南京市', 'city_code': 315, 'district': '', 'province': '江苏省', 'street': '', 'street_number': ''}, 'point': {'x': '118.80242172', 'y': '32.06465289'}}, 'status': 0}
    print(result)
    #包括省、市、区县、街道等
    print(result["address"])
    print(result["content"]["address_detail"]["province"])
    print(result["content"]["address_detail"]["city"])
    print(result["content"]["address_detail"]["district"])
    print(result["content"]["address_detail"]["street"])
    print(result["content"]["address_detail"]["street_number"])
else:
    print("查询失败，错误码：" + result["status"])
