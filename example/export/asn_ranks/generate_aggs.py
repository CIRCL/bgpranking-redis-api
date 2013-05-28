#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import urllib2
from bgpranking import tools


csv_dir = os.path.join('..', '..', 'website', 'data', 'csv')
agg_csv_dir = os.path.join('..', '..','website', 'data', 'csv_agg')
js_dir = os.path.join('..', '..', 'website', 'data', 'js')

ripe_url_be = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=be'
ripe_url_de = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=de'
ripe_url_lu = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=lu'
ripe_url_fr = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=fr'
ripe_url_nl = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=nl'

def get_announces(ripe_url):
    handle = urllib2.urlopen(ripe_url, timeout=10)
    json_dump = handle.read()
    data = json.loads(json_dump)
    asns = data['data']['resources']['asn']
    return asns

if __name__ == '__main__':
    be_asns = get_announces(ripe_url_be)
    de_asns = get_announces(ripe_url_de)
    lu_asns = get_announces(ripe_url_lu)
    fr_asns = get_announces(ripe_url_fr)
    nl_asns = get_announces(ripe_url_nl)
    tools.aggregate_csvs(csv_dir, agg_csv_dir, with_world = False,
            **{ 'belgium':be_asns, 'germany': de_asns, 'luxembourg': lu_asns,
                'france': fr_asns, 'netherlands': nl_asns})
    tools.aggregate_csvs(csv_dir, agg_csv_dir, **{'luxembourg': lu_asns})
    tools.generate_dumps_for_worldmap(js_dir, agg_csv_dir)
