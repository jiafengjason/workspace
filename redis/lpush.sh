#!/bin/bash

for ((i=0;i<100000;i++))
do
    echo -en www.name$i.com | redis-cli -a enlink -x LPUSH runoobkey >>redis.log
done