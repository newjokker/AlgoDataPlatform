#!/bin/bash

source ~/.bash_aliases

service redis-server start

./stop_server.sh

rm ./logs/*

supervisord -c ./confd.conf

# tail -f /dev/null



