#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import bgpranking


if __name__ == '__main__':

    r = redis.Redis(unix_socket_path='./redis_export.sock')
    date = r.get('date')
    weights = bgpranking.get_all_weights(date)
    while True:
        asn_b = r.spop('asn_b')
        if asn_b is None:
            break
        asn, block = asn_b.split("_")
        ip_descs = bgpranking.get_ips_descs(asn, block, date)
        if len(ip_descs.get(block)) != 0:
            p = r.pipeline(False)
            for ip, sources in ip_descs.get(block).iteritems():
                p.zincrby('ips', ip, sum([float(weights[s]) for s in sources]))
                p.hmset(ip, {'asn': asn, 'block':block,
                    'sources': '|'.join(sources)})
            p.execute()


