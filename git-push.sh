#!/bin/sh

if [ "$1" = "-h" ]; then
    echo "git-push.sh [ -h | -y ]"
    exit
fi

dir=`dirname $0`
echo "Directory: $dir"

git status

if [ "$1" != "-y" ]; then
    read -p "Push? [Y/n]" push
fi

if [ "$1" = "-y" -o "$push" != "n" ]; then
    git add $dir && git commit -m "update" 
    git pull && git push
fi
