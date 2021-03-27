#coding=utf-8

import http.client
import time
import os
from apscheduler.schedulers.blocking import BlockingScheduler

def job():
    pass

def getWebserverTime(host):
    conn=http.client.HTTPConnection(host)
    conn.request("GET", "/")
    r=conn.getresponse()
    print(r.status, r.reason)
    
    #r.getheaders() #获取所有的http头
    ts = r.getheader('date') #获取http头date部分
    #将GMT时间转换成北京时间
    ltime= time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
    print(ltime)
    ttime=time.localtime(time.mktime(ltime)+8*60*60)
    print(ttime)
    tm='date -s "%u-%02u-%02u %02u:%02u:%02u"' % (ttime.tm_year,ttime.tm_mon,ttime.tm_mday,ttime.tm_hour,ttime.tm_min,ttime.tm_sec)
    print(tm)
    os.system(tm)

if __name__=='__main__':
    getWebserverTime('www.baidu.com')
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'cron', day_of_week='0-6', hour=20, minute=00, timezone='Asia/Shanghai')
    scheduler.start()