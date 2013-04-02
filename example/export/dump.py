#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis

if __name__ == '__main__':
    r = redis.Redis(unix_socket_path='./redis_export.sock')
    with open('ips', 'w') as f:
        ips = r.smembers('ips')
        for ip in ips:
            f.write(ip + '\n')

# cat ips | sort -n -t . -k 1,1 -k 2,2 -k 3,3 -k 4,4 | uniq >> sorted-ips
