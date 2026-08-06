#!/bin/bash

cmd='/home/enlink/sdp-gateway/bin/redis-cli'

if [ ! -f "$cmd" ]; then
    cmd='redis-cli'
fi

for i in {0..20000}
do
    acc='test'$i
    echo $acc
    key=`echo -n $acc | md5sum | awk '{print $1}'`
    echo $key
    session='enlink:gate:http:session:'$key
    #$cmd -a enlink set $session 1
	$cmd -a enlink HSET $session "profile" "{\"account\":\"$acc\",\"name\":\"$acc\",\"group\":\"\",\"device\":\"$session\",\"terminalInfo\":\"EnUES\",\"region\":\"$i\",\"tid\":\"10000000\",\"score\":\"100.0\"}"
	$cmd -a enlink HSET $session "grouppolicys" "user_group_202408021652521819295288424443049000;role_202409301037121840581634080355586000;user_group_all;user_group_0;globalWhite"
done
