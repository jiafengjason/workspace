import json
import redis
from openpyxl import Workbook

count = {}
stat = {}

def get_redis_data(workbook, r, key):
    data = None
    index = 1
    
    sheet_name = key.split(":")[-1]
    #print(sheet_name)
    sheet = workbook.create_sheet(title=sheet_name)
    
    typ = r.type(key).decode('utf-8')
    if typ == "hash":
        data = r.hgetall(key)  # 替换为你的Redis key
        for key, value in data.items():
            sheet['A'+str(index)] = key
            sheet['B'+str(index)] = value
            index += 1
    elif typ == "set":
        data = r.smembers(key)
        for value in data:
            value = value.decode('utf-8').strip()
            sheet['A'+str(index)] = value
            index += 1
            if value in count:
                count[value].append(sheet_name)

# Redis连接信息
redis_host = 'localhost'
redis_port = 6378
redis_password = 'enlink'  # 如果没有设置密码，可以将此行注释掉

# Excel文件路径
excel_file = 'redis_data.xlsx'

# 连接Redis
r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

with open('tb_device_program.json', 'r') as f:
    data = json.load(f)
    for item in data:
        count[item["id"]] = []

workbook = Workbook()
sheet = workbook.active
workbook.remove(sheet)
keys = r.keys(pattern="terminal:deviceProgramMp:*")
for key in keys:
    get_redis_data(workbook, r, key.decode('utf-8'))

# 保存Excel文件
#workbook.save(excel_file)
print(f"Redis数据已成功写入Excel文件：{excel_file}")

with open('tb_device_program.json', 'r') as f:
    data = json.load(f)
    for item in data:
        stat[item["name"]] = count[item["id"]]
        #print("%s:%d\r\n" % (item["name"], count[item["id"]]))

with open('stat.json', 'w') as json_file:
    json.dump(stat, json_file, ensure_ascii=False, indent=4)
