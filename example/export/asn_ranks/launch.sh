#!/bin/bash

while true; do
    echo ----- New Run -----
    date
    bash ./launch_local_redis.sh
    echo -n 'Preparing Redis database... '
    python ./init_redis.py
    echo 'done.'

    date
    echo -n 'Exporting ranks to CSV... '
    for i in {1..10}; do
        python ./consumer.py &
    done
    echo 'done.'
    date

    python ./consumer.py
    sleep 10

    redis-cli -s ./redis_export.sock shutdown

    echo -n 'Building aggregations... '
    python ./generate_aggs.py
    echo 'done.'
    date

    echo ----- End of Run. -----
    sleep 10000
done
