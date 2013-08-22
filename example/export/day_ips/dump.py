#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import csv
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dump on the disk the daily informations.')
    parser.add_argument('-f', '--full', action="store_true", default=False,
            help='Do a full dump (asn, block, ip, sources).')
    args = parser.parse_args()

    r = redis.Redis(unix_socket_path='./redis_export.sock')
    date = r.get('date')
    with open('ips_' + date, 'w') as f:
        ips = list(r.zrange('ips', 0, -1))
        for i in range(len(ips)):
            ips[i] = "%3s.%3s.%3s.%3s" % tuple(ips[i].split("."))
        ips.sort()
        for i in range(len(ips)):
            ips[i] = ips[i].replace(" ", "")
        p = r.pipeline(False)
        [p.zscore('ips', ip) for ip in ips]
        weights = p.execute()
        [f.write(','.join(map(str, iw)) + '\n') for iw in zip(ips, weights)]
    if args.full:
        with open('full_' + date, 'wb') as f:
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
