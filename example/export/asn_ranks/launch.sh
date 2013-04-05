#!/bin/bash

while true; do
    bash ./launch_local_redis.sh
    echo 'Preparing Redis database'
    python ./init_redis.py
    echo 'Done.'

    date
    echo 'Exporting ranks to CSV....'
    for i in {1..10}; do
        python ./consumer.py &
    done

    python ./consumer.py
    echo 'Export finished.'
    date
    sleep 10

    redis-cli -s ./redis_export.sock shutdown

    echo 'Building aggregations...'
    python ./generate_aggs.py
    echo 'Done.'
    date

    sleep 10000
done
