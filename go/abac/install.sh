#!/bin/bash

CURRENT=`pwd`

service abac stop

cp -rf ${CURRENT}/etc/* /etc
systemctl daemon-reload
systemctl enable abac

service abac start


