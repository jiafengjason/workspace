#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Run on python2.X
create 300000 files (512B to 1536B) with data from /dev/urandom
rewrite 30000 random files and change the size
read 30000 sequential files
read 30000 random files
'''

import random, time
from os import system

filecount = 100
filesize = 1024*1024

flush = "su -c 'sync ; echo 3 > /proc/sys/vm/drop_caches'"
randfile = open("/dev/urandom", "r")

print("\ncreate test folder:")
stime = time.time()
system("rm -rf test && mkdir test")
etime = time.time()
duration = etime - stime
print(duration)
system(flush)

print("\ncreate files:")
total = 0
stime = time.time()
for i in range(filecount):
    size = int(filesize * 0.5 + filesize * random.random())
    rand = randfile.read(size)
    outfile = open("test/" + unicode(i), "w")
    outfile.write(rand)
    total += size
etime = time.time()
duration = etime - stime
print(duration, total/1024/1024/duration)
system(flush)

'''
print("\nrewrite files:")
total = 0
stime = time.time()
for i in range(int(filecount / 10)):
    rand = randfile.read(int(filesize * 0.5 + filesize * random.random()))
    outfile = open("test/" + unicode(int(random.random() * filecount)), "w")
    outfile.write(rand)
    total += size
etime = time.time()
duration = etime - stime
print(duration, total/1024/1024/duration)
system(flush)
'''

print("\nread linear:")
stime = time.time()
for i in range(filecount):
    infile = open("test/" + unicode(i), "r")
    outfile.write(infile.read());
etime = time.time()
duration = etime - stime
print(duration, total/1024/1024/duration)
system(flush)

'''
print("\nread random:")
stime = time.time()
outfile = open("/dev/null", "w")
for i in range(int(filecount / 10)):
    infile = open("test/" + unicode(int(random.random() * filecount)), "r")
    outfile.write(infile.read());
etime = time.time()
duration = etime - stime
print(duration, total/1024/1024/duration)
system(flush)
'''

print("\ndelete all files:")
stime = time.time()
system("rm -rf test")
etime = time.time()
duration = etime - stime
print(duration)
system(flush)
