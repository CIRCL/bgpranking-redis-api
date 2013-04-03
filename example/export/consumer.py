#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import bgpranking


if __name__ == '__main__':

    r = redis.Redis(unix_socket_path='./redis_export.sock')
    date = r.get('date')
    while True:
        asn_ts= r.spop('asn_ts')
        if asn_ts is None:
            break
        asn, ts = asn_ts.split("_")
        ip_descs = bgpranking.get_ips_descs(asn, ts, date)
        if len(ip_descs.get(ts)) != 0:
            p = r.pipeline(False)
            block = bgpranking.get_block(asn, ts)
            for ip, sources in ip_descs.get(ts).iteritems():
                p.sadd('ips', ip)
                p.hmset(ip, {'asn': asn, 'block':block,
                    'sources': '|'.join(sources)})
            p.execute()


