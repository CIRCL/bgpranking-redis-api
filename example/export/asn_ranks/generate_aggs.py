#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import urllib2
from bgpranking import tools


csv_dir = os.path.join('..', '..', 'website', 'data', 'csv')
agg_csv_dir = os.path.join('..', '..','website', 'data', 'csv_agg')
js_dir = os.path.join('..', '..', 'website', 'data', 'js')

ripe_url = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=lu'

def get_announces():
    handle = urllib2.urlopen(ripe_url, timeout=10)
    json_dump = handle.read()
    data = json.loads(json_dump)
    asns = data['data']['resources']['asn']
    return asns

if __name__ == '__main__':
    lu_asns = get_announces()
    tools.aggregate_csvs(csv_dir, agg_csv_dir, **{'luxembourg': lu_asns})
    tools.generate_dumps_for_worldmap(js_dir, agg_csv_dir)
