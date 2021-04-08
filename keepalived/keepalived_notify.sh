#!/bin/bash

echo $(date +%F%n%T) $1 $2 is in $3 state >> /var/log/keepalived.log
