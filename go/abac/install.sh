#!/bin/bash

service abac stop

cp -rf abac.service /etc/systemd/system
systemctl daemon-reload
systemctl enable abac

service abac start


