#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from bgpranking import tools

csv_dir = os.path.join('data', 'csv')
tools.prepare_all_csv(csv_dir)

agg_csv_dir = os.path.join('data', 'csv_agg')
# cat LU-overall-allocv4-v6-asn.txt | grep asn | cut -d "|" -f 4
lu_raw_asns = open('lu_asns_dump', 'r').read()
lu_asns = lu_raw_asns.split('\n')

tools.aggregate_csvs(csv_dir, agg_csv_dir, **{'luxembourg': lu_asns})

js_dir = os.path.join('data', 'js')
tools.generate_js_for_worldmap(js_dir)
