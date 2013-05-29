#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import urllib2
from bgpranking import tools
from csv import DictWriter


import argparse
import glob
import redis


csv_dir = os.path.join('..', '..', 'website', 'data', 'csv')
agg_csv_dir = os.path.join('..', '..','website', 'data', 'csv_agg')
js_dir = os.path.join('..', '..', 'website', 'data', 'js')

ripe_url = 'https://stat.ripe.net/data/country-resource-list/data.json?resource={cc}'

def get_announces(ripe_url):
    handle = urllib2.urlopen(ripe_url, timeout=10)
    json_dump = handle.read()
    data = json.loads(json_dump)
    asns = data['data']['resources']['asn']
    return asns

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Bunch of function to create aggregations')
    parser.add_argument('-pka', '--push_known_asns', action='store_true',
            default=False)
    parser.add_argument('-cc', '--country_codes', nargs='+', type=str)
    parser.add_argument('-dcc', '--dump_country_codes', nargs='+', type=str)
    parser.add_argument('-map' '--make_map', action='store_true', default=False)
    args = parser.parse_args()
    r = redis.Redis(unix_socket_path='./redis_export.sock')

    if args.push_known_asns:
        csv_files = glob.glob(os.path.join(csv_dir, '*'))
        p = r.pipeline(False)
        [p.sadd('known_asns', csv_file) for csv_file in csv_files]
        p.execute()
        print 'Number of asns:', len(csv_file)
        return True
    if args.country_codes is not None and len(args.country_codes) > 0:
        p = r.pipeline(False)
        p.sadd('countries', *args.country_codes)
        for cc in args.country_codes:
            url = ripe_url.format(cc=cc)
            asns = get_announces(url)
            p.sadd(cc, *asns)
        p.execute()
        return True
    if args.dump_country_codes is not None and len(args.dump_country_codes) > 0:
        filename = os.path.join(agg_csv_dir, '_'.join(args.dump_country_codes))
        with open(filename, 'w') as f:
            w = DictWriter(f, fieldnames= ['date'] + args.dump_country_codes)
            w.writeheader()
            for date in r.smembers('days'):
                entries = r.hgetall(date)
                entries.update({'date': date})
                w.writerow(entries)
        return True
    if args.make_map:
        tools.generate_dumps_for_worldmap(js_dir, agg_csv_dir)
        return True

