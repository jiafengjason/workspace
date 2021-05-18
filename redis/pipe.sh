#!/bin/bash

while read LINE; do
    # each command begins with *{number arguments in command}\r\n
    XS=($LINE); printf "*${#XS[@]}\r\n"
    # for each argument, we append ${length}\r\n{argument}\r\n
    for X in $LINE; do printf "\$${#X}\r\n$X\r\n"; done
done < redis_pipe_commands.txt