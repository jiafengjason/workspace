#!/usr/bin/python
#coding=utf-8

from datetime import datetime
import time
import os

if os.path.exists("redis_lpush_commands.txt"):
    os.remove('redis_lpush_commands.txt')
if os.path.exists("redis_pipe_commands.txt"):
    os.remove('redis_pipe_commands.txt')
if os.path.exists("redis_data.txt"):
    os.remove('redis_data.txt')
os.system("redis-cli -a enlink del batchLpush")
os.system("redis-cli -a enlink del batchPipe")

startTime = datetime.now()
with open('redis_lpush_commands.txt', 'w') as f:
    f.write("LPUSH batchLpush ")
    for i in range(100000):
        f.write("www.name%s.com " % str(i))
endTime = datetime.now()
duration = (endTime-startTime).microseconds
print("Generate redis lpush commands:%dms" % (duration/1000))

startTime = datetime.now()
with open('redis_pipe_commands.txt', 'w') as f:
    f.write("LPUSH batchPipe ")
    for i in range(100000):
        f.write("www.name%s.com " % str(i))
    f.write("\n")
endTime = datetime.now()
duration = (endTime-startTime).microseconds
print("Generate redis pipe commands:%dms" % (duration/1000))

startTime = datetime.now()
os.system("sh pipe.sh > redis_data.txt")
endTime = datetime.now()
duration = (endTime-startTime).microseconds
print("Change to redis protocol:%dms" % (duration/1000))

startTime = datetime.now()
os.system("time cat redis_lpush_commands.txt | redis-cli -a enlink -x")
endTime = datetime.now()
duration = (endTime-startTime).microseconds
print("Lpush:%dms" % (duration/1000))

startTime = datetime.now()
os.system("time cat redis_data.txt | redis-cli -a enlink --pipe")
endTime = datetime.now()
duration = (endTime-startTime).microseconds
print("Pipe:%dms" % (duration/1000))

