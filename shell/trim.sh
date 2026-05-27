#!/bin/bash

var="ExecStart=/home/sdpgate2.0/release/latest/enlink/bin/gate-start.sh"
var=${var#*=}
var=${var%/*}
echo $var
