#!/bin/bash

source ~/.bash_aliases

service redis-server start

./stop_server.sh

supervisord -c ./confd.conf

tail -f /dev/null



