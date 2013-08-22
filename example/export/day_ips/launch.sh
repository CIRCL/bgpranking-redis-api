#!/bin/bash

while read date ; do

    echo $date
    bash ./launch_local_redis.sh
    python ./init_redis.py -d $date

    date
    for i in {1..10}; do
        python ./consumer.py &
    done

    python ./consumer.py
    date
    sleep 10

    python ./dump.py
    date
done < dates.txt
