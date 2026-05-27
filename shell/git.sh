#!/bin/bash

cd $1
total=0
for dir in $(find . -maxdepth 1 -type d ); do
    [[ "$dir" == "." || "$dir" == ".." ]] && continue
    echo $dir
    cd $dir
    sum=`git log --since=2024-01-01 --until=2024-12-31 --author="jiafeng" --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; sum += $1 + $2 } END { printf "%s", sum }'`
    total=$((total + sum))
    cd -
done

echo $total
