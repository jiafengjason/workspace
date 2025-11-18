#coding=utf-8
from datetime import datetime, timedelta
import math
import requests
import schedule
import sys
import time

def local_time():
    ts = datetime.now().timestamp()
    return ts * 1000
    
def format_time(timestamp, formater):
    # 使用datetime.fromtimestamp()方法将时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(timestamp/1000.0)
      
    # 使用strftime()方法将datetime对象格式化为字符串  
    formatted_time = dt_object.strftime(formater)
    return formatted_time

def jd_time():
    start_time = datetime.now()
    url = 'https://api.m.jd.com'
    resp = requests.get(url)
    requestId = resp.headers.get('X-API-Request-Id')
    jd_timestamp = int(requestId[-13:])
    print('jd_timestamp:' + str(jd_timestamp))
    end_time = datetime.now()
    req_time = end_time - start_time
    duration = req_time.microseconds/1000
    print('单次请求时间:' + str(duration) + 'ms')
    if duration > 500:
        print('单次请求时间过长很难抢到')
    return jd_timestamp

def jd_local_time_diff():
    jdTime = jd_time()
    localTime = local_time()
    cha = jdTime - localTime
    print('服务器时间: ' + format_time(jdTime, '%Y-%m-%d %H:%M:%S.%f'))
    print('本机时间:   ' + format_time(localTime, '%Y-%m-%d %H:%M:%S.%f'))
    print('JD服务器与本机时间差值为：' + str(cha) + ' ms')
    if abs(cha / 1000.0) >= 5:
        print('时间差值过大，建议先同步下时间再重启下软件')
    return cha

def task_time(time_str, sec):
    time_format = '%H:%M:%S'
    time_object = datetime.strptime(time_str, time_format)
    return datetime.strftime(time_object + timedelta(seconds=-sec), time_format)

if __name__ == '__main__':
    cha = jd_local_time_diff()
    # jd时间比本机快，job启动时间就要比预定时间要早
    cha_time = math.ceil(cha / 1000.0)
    schedule.every().day.at(task_time("17:22:00", cha_time)).do(jd_local_time_diff)

    while True:
        schedule.run_pending()
        time.sleep(1)