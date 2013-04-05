#!/usr/bin/python
# -*- coding: utf-8 -*-

import bgpranking
import redis

interval_size = 800

if __name__ == '__main__':

    dates_sources = bgpranking.prepare_sources_by_dates(None, interval_size)
    asns = bgpranking.existing_asns_timeframe(dates_sources)

    r = redis.Redis(unix_socket_path='./redis_export.sock')
    r.set('interval_size', interval_size)
    r.mset('asns', *asns)

