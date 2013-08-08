#!/bin/bash

bash ./launch_local_redis.sh
python ./init_redis.py

date
for i in {1..10}; do
    python ./consumer.py &
done

python ./consumer.py
date
sleep 10

python ./dump.py
date
