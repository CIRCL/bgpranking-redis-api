#!/usr/bin/python
# -*- coding: utf-8 -*-

from csv import writer
import os
import glob
from csv import DictReader, DictWriter
from socket import socket, AF_INET, SOCK_STREAM
import json

import bgpranking

def prepare_all_csv(output_csv_dir, interval = 1000, force = False):
    """
        Make CSV files for all the ASNs ranked during the interval.
    """
    keepdir_path = os.path.join(output_csv_dir, '.is_csv_dir')
    if not os.path.exists(output_csv_dir):
        os.mkdir(output_csv_dir)
    if force:
        open(keepdir_path, 'w').close()
    if not os.path.exists(keepdir_path):
         print('Wrong dir.')
         exit()
    dates_sources = bgpranking.prepare_sources_by_dates(None, interval)
    asns = bgpranking.existing_asns_timeframe(dates_sources)
    for asn in asns:
        filename = os.path.join(output_csv_dir, asn)
        with open(filename, 'w') as csvfile:
            w = writer(csvfile)
            w.writerow(['day', 'rank'])
            ranks = bgpranking.get_all_ranks_single_asn(asn, dates_sources)
            for date, entry in ranks.iteritems():
                w.writerow([date, 1 + entry['total']])

def aggregate_csvs(output_csv_dir, output_agg_dir, **kwargs):
    """
        Aggregate lists of ASNs in a single CSV file.

        kwargs has to be like:
            list_name_1 = [list of asns], list_name_2 = [list of asns]

        The output CSV file will have this format:
            date, world, list_name_1, list_name_2, ....
    """
    csv_files = glob.glob(os.path.join(output_csv_dir, '*'))
    result = {}
    for csv_file in csv_files:
        asn = os.path.basename(csv_file)
        with open(csv_file, 'r') as f:
            reader = DictReader(f)
            for entry in reader:
                # Removing 1 because we aggregate data
                rank = float(entry['rank']) -1
                if result.get(entry['day']) is None:
                    result[entry['day']] = {}
                if result[entry['day']].get('world') is None:
                    result[entry['day']]['world'] = 0
                result[entry['day']]['world'] += rank
                for key, arg in kwargs.iteritems():
                    if asn in arg:
                        if result[entry['day']].get(key) is None:
                            result[entry['day']][key] = 0
                        result[entry['day']][key] += rank
    fieldnames = ['world'] + kwargs.keys()
    filename = os.path.join(output_agg_dir, '_'.join(fieldnames))
    with open(filename, 'w') as f:
        w = DictWriter(f, fieldnames= ['date'] + fieldnames)
        w.writeheader()
        for date, entries in result.iteritems():
            entries.update({'date': date})
            w.writerow(entries)

def get_asns_country_code(asns):
    text_lines = ["begin", "verbose"]
    [text_lines.append("AS" + asn) for asn in asns]
    text_lines.append("end")
    text = '\n'.join(text_lines) + '\n'

    s = socket(AF_INET, SOCK_STREAM)
    s.connect(("whois.cymru.com", 43))
    s.send(text)
    response = ''
    data = s.recv(2048)
    while data:
        response += data
        data = s.recv(2048)
    s.close()
    to_return = {}
    splitted = response.split('\n')
    for r in splitted[1:-1]:
        s = r.split("|")
        asn = s[0].strip()
        cc = s[1].strip()
        to_return[asn] = cc
    return to_return

def generate_js_for_worldmap(output_dir):
    ranks = bgpranking.cache_get_top_asns(limit = -1, with_sources = False)
    if ranks.get('top_list') is not None:
        info = get_asns_country_code([asn for asn, rank in ranks.get('top_list')])
        to_dump = {}
        for asn, rank in ranks.get('top_list'):
            cc = info[asn]
            if to_dump.get(cc) is None:
                to_dump[cc] = 0
            to_dump[cc] += rank

        f = open(os.path.join(output_dir, 'worldmap.js'), "w")
        f.write("var ranks =\n" + json.dumps(to_dump))
        f.close()


