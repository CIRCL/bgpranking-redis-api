#!/usr/bin/python
# -*- coding: utf-8 -*-

import bgpranking
import argparse

import redis

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a list of all IPS for a day.')
    parser.add_argument('-d', '--date', default=None, help='Date of the dump (YYYY-MM-DD)')

    args = parser.parse_args()
    date = args.date

    if date is None:
        date = bgpranking.get_default_date()

    dates_sources = bgpranking.prepare_sources_by_dates(date, 1)

    asns = bgpranking.existing_asns_timeframe(dates_sources)

    r = redis.Redis(unix_socket_path='./redis_export.sock')
    r.set('date', date)
    for asn in asns:
        blocks = bgpranking.get_all_blocks(asn)
        p = r.pipeline(False)
        for b in blocks:
            p.sadd('asn_b', "{asn}_{b}".format(asn=asn, b=b))
        p.execute()

