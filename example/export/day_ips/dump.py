#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import csv

if __name__ == '__main__':
    r = redis.Redis(unix_socket_path='./redis_export.sock')
    with open('ips', 'w') as f:
        ips = list(r.zrange('ips', 0, -1))
        for i in range(len(ips)):
            ips[i] = "%3s.%3s.%3s.%3s" % tuple(ips[i].split("."))
        ips.sort()
        for i in range(len(ips)):
            ips[i] = ips[i].replace(" ", "")
        p = r.pipeline(False)
        [p.zscore('ips', ip) for ip in ips]
        weights = p.execute()
        [f.write(','.join(iw) + '\n') for iw in zip(ips, weights)]
    with open('full', 'wb') as f:
        w = csv.writer(f)
        ips = r.zrange('ips', 0, -1)
        p = r.pipeline(False)
        [p.hgetall(ip) for ip in ips]
        all_entries = p.execute()
        i = 0
        for entries in all_entries:
            w.writerow([entries['asn'], entries['block'], ips[i],
                entries['sources']])
            i += 1
    r.shutdown()
