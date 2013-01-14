#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time

from bgpranking import tools

csv_dir = os.path.join('..', 'data', 'csv')
agg_csv_dir = os.path.join('..', 'data', 'csv_agg')
js_dir = os.path.join('..', 'data', 'js')


while True:
    tools.prepare_all_csv(csv_dir)

    # cat LU-overall-allocv4-v6-asn.txt | grep asn | cut -d "|" -f 4
    lu_raw_asns = open('lu_asns_dump', 'r').read()
    lu_asns = lu_raw_asns.split('\n')

    tools.aggregate_csvs(csv_dir, agg_csv_dir, **{'luxembourg': lu_asns})

    tools.generate_dumps_for_worldmap(js_dir, agg_csv_dir)

    time.sleep(10000)
