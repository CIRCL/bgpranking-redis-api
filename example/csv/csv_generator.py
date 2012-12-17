#!/usr/bin/python
# -*- coding: utf-8 -*-


from csv import writer
import os
import shutil
import bgpranking

directory = 'csv'


def init_all_csv(interval = 365):
    keepdir_path = os.path.join(directory, '.keepdir')
    if os.path.exists(directory):
        if os.path.exists(os.path.join(directory, '.keepdir')):
            shutil.rmtree(directory)
        else:
            print('Wrong dir.')
            exit()
    os.mkdir(directory)
    open(keepdir_path, 'w').close()
    dates_sources = bgpranking.prepare_sources_by_dates(None, interval)
    asns = bgpranking.existing_asns_timeframe(dates_sources)
    for asn in asns:
        filename = os.path.join(directory, asn)
        with open(filename, 'w') as csvfile:
            w = writer(csvfile)
            w.writerow(['day', 'rank'])
            ranks = bgpranking.get_all_ranks_single_asn(asn, dates_sources)
            for date, entry in ranks.iteritems():
                w.writerow([date, 1 + entry['total']])

if __name__ == '__main__':
    init_all_csv(2)
