#!/usr/bin/python
# -*- coding: utf-8 -*-

from csv import DictReader
import redis
import os

if __name__ == '__main__':
    r = redis.Redis(unix_socket_path='./redis_export.sock')
    countries = r.smembers('countries')
    cached_asns = {}
    for cc in countries:
        cached_asns[cc] = r.smembers(cc)
    while True:
        csv_file = r.spop('known_asns')
        if csv_file is None:
            break
        asn = os.path.basename(csv_file)
        with open(csv_file, 'r') as f:
            reader = DictReader(f)
            p = r.pipeline(False)
            for entry in reader:
                p.sadd('days', entry['day'])
                # Removing 1 because we aggregate data
                rank = float(entry['rank']) - 1
                p.hincrbyfloat(entry['day'], 'world', rank)
                for cc in countries:
                    if asn in cached_asns[cc]:
                        p.hincrbyfloat(entry['day'], cc, rank)
                        break
            p.execute()

