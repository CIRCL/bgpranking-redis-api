#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import bgpranking
import os
from csv import writer

csv_dir = os.path.join('..', '..', 'website', 'data', 'csv')

if __name__ == '__main__':

    r = redis.Redis(unix_socket_path='./redis_export.sock')
    interval = int(r.get('interval_size'))
    dates_sources = bgpranking.prepare_sources_by_dates(None, interval)
    while True:
        asn = r.spop('asns')
        if asn is None:
            break
        filename = os.path.join(csv_dir, asn)
        with open(filename, 'w') as csvfile:
            w = writer(csvfile)
            w.writerow(['day', 'rank'])
            ranks = bgpranking.get_all_ranks_single_asn(asn, dates_sources)
            for date, entry in ranks.iteritems():
                w.writerow([date, 1 + entry['total']])



