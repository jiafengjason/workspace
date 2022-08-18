#!/bin/bash

service abac stop

cp -rf abac.service /etc/systemd/system
systemctl daemon-reload
systemctl daemon-reload

service abac start


