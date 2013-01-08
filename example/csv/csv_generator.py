#!/usr/bin/python
# -*- coding: utf-8 -*-


from csv import writer
import os
import shutil
import glob
from csv import DictReader, DictWriter

import bgpranking

directory = 'csv'
agg_directory = 'aggregated'

def prepare_all_csv(interval = 730):
    """
        Make CSV files for all the ASNs ranked during the interval.
    """
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

def aggregate(**kwargs):
    """
        Aggregate lists of ASNs in a single CSV file.

        kwargs has to be like:
            list_name = [list of asns], list_name = [list of asns]
    """
    csv_files = glob.glob(os.path.join(directory, '*'))
    result = {}
    for csv_file in csv_files:
        asn = os.path.basename(csv_file)
        with open(csv_file, 'r') as f:
            reader = DictReader(f)
            for entry in reader:
                if result.get(entry['day']) is None:
                    result[entry['day']] = {}
                if result[entry['day']].get('world') is None:
                    result[entry['day']]['world'] = 0
                result[entry['day']]['world'] += float(entry['rank'])
                for key, arg in kwargs.iteritems():
                    if asn in arg:
                        if result[entry['day']].get(key) is None:
                            result[entry['day']][key] = 0
                        result[entry['day']][key] += float(entry['rank'])
    fieldnames = ['world'] + kwargs.keys()
    filename = os.path.join(agg_directory, '_'.join(fieldnames))
    with open(filename, 'w') as f:
        w = DictWriter(f, fieldnames= ['date'] + fieldnames)
        w.writeheader()
        for date, entries in result.iteritems():
            entries.update({'date': date})
            w.writerow(entries)

if __name__ == '__main__':
    #prepare_all_csv(2)
    aggregate(luxembourg=["5577", "6661"], france=["16276"])
