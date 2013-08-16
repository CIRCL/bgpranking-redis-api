#!/bin/bash

LIST_DATES="2012-01-01 2012-02-01 2012-03-01 2012-04-01 2012-05-01 2012-06-01
2012-07-01 2012-08-01 2012-09-01 2012-10-01 2012-11-01 2012-12-01 2013-01-01
2013-02-01 2013-03-01 2013-04-01 2013-05-01 2013-06-01 2013-07-01 2013-08-01"

for date in ${LIST_DATES}; do

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
done
