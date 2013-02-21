#!/usr/bin/python
# -*- coding: utf-8 -*-

import bgpranking
import argparse
import csv

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a list of all IPS for a day.')
    parser.add_argument('-d', '--date', default=None, help='Date of the dump (YYYY-MM-DD)')

    args = parser.parse_args()
    date = args.date

    if date is None:
        date = bgpranking.get_default_date()

    dates_sources = bgpranking.prepare_sources_by_dates(date, 1)

    asns = bgpranking.existing_asns_timeframe(dates_sources)
    with open(date, 'w') as f:
        w = csv.writer(f)
        for asn in asns:
            timestamps = bgpranking.get_all_asn_timestamps(asn)
            for ts in timestamps:
                block = bgpranking.get_block(asn, ts)
                ip_descs = bgpranking.get_ips_descs(asn, ts, date)
                if len(ip_descs.get(ts)) != 0:
                    for ip, sources in ip_descs.get(ts).iteritems():
                        entry = [asn, block, ip, '|'.join(sources)]
                        w.writerow(entry)

