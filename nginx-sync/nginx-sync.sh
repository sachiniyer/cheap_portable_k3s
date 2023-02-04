#!/bin/bash

wget -q https://raw.githubusercontent.com/sachiniyer/cheap_portable_k3s/main/nginx.conf -O /tmp/nginx.conf

diff=$(sdiff -s /tmp/nginx.conf /usr/local/nginx/conf/nginx.conf)

if [ -n "$diff" ]; then
    echo "Try to changing"
    mv /usr/local/nginx/conf/nginx.conf /usr/local/nginx/conf/nginx.conf.save
    mv /tmp/nginx.conf /usr/local/nginx/conf/nginx.conf
    if /usr/local/nginx/sbin/nginx -t; then
        systemctl reload nginx
        echo "Success"
    else
        mv /usr/local/nginx/conf/nginx.conf.save /usr/local/nginx/conf/nginx.conf
        echo "Failure"
    fi
else
    echo "It is the same"
fi
