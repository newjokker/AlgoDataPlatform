#!/bin/bash

rm -r ./logs/*
mkdir -p ./logs
mkdir -p ./logs/supervisord

source ~/.bash_aliases

service redis-server start

./stop_server.sh

supervisord -c ./confd.conf

tail -f /dev/null



