#!/usr/bin/python
# -*- coding: utf-8 -*-


from csv import writer
import os
import shutil
import bgpranking

directory = 'csv'


def init_all_csv(interval = 365):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    dates_sources = bgpranking.prepare_sources_by_dates(None, interval)
    all_ranks = bgpranking.get_all_ranks_all_asns(dates_sources)
    for date, asns in all_ranks.iteritems():
        for asn, values in asns.iteritems():
            rank = values['total']
            filename = os.path.join(directory, asn)
            if not os.path.exists(filename):
                with open(filename, 'w') as csvfile:
                    w = writer(csvfile)
                    w.writerow(['day', 'rank'])
                    w.writerow([date, 1 + rank])
            else:
                with open(filename, 'a') as csvfile:
                    w = writer(csvfile)
                    w.writerow([date, 1 + rank])


if __name__ == '__main__':
    init_all_csv(2)
