#!/bin/bash

HOME="/home/raphael/"

REDIS_SERVER="${HOME}/gits/redis/src/redis-server"

${REDIS_SERVER} ./redis.conf
