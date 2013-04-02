#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import bgpranking


if __name__ == '__main__':

    r = redis.Redis(unix_socket_path='./redis_export.sock')
    date = r.get('date')
    while True:
        asn = r.spop('asn')
        if asn is None:
            break
        timestamps = bgpranking.get_all_asn_timestamps(asn)
        p = r.pipeline(False)
        for ts in timestamps:
            ip_descs = bgpranking.get_ips_descs(asn, ts, date)
            if len(ip_descs.get(ts)) != 0:
                block = bgpranking.get_block(asn, ts)
                for ip, sources in ip_descs.get(ts).iteritems():
                    p.sadd('ips', ip)
                    p.hmset(ip, {'asn': asn, 'block':block,
                        'sources': '|'.join(sources)})
        p.execute()


