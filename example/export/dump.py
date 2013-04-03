#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import csv

if __name__ == '__main__':
    r = redis.Redis(unix_socket_path='./redis_export.sock')
    with open('ips', 'w') as f:
        ips = list(r.smembers('ips'))
        for i in range(len(ips)):
            ips[i] = "%3s.%3s.%3s.%3s" % tuple(ips[i].split("."))
        ips.sort()
        for i in range(len(ips)):
            ips[i] = ips[i].replace(" ", "")
        for ip in ips:
            f.write(ip + '\n')
    with open('full', 'wb') as f:
        w = csv.writer(f)
        ips = r.smembers('ips')
        for ip in ips:
            entries = r.hgetall(ip)
            w.writerow([entries['asn'], entries['block'], ip, entries['sources']])
    #r.shutdown()


# cat ips | sort -n -t . -k 1,1 -k 2,2 -k 3,3 -k 4,4 | uniq >> sorted-ips
