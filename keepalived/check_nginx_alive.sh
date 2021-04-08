#!/bin/sh

PATH=/bin:/sbin:/usr/bin:/usr/sbin

echo "check_nginx_alive"
A=`ps -C nginx --no-header |wc -l`

if [ $A -eq 0 ]; then
    echo 'nginx server is died'
    # killall keepalived
    exit 1
fi

exit 0
