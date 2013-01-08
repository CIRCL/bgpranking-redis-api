#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Map
    ~~~

    Generate the data used to display the world map
"""

from socket import socket, AF_INET, SOCK_STREAM
import json
import os

import bgpranking

output_file = os.path.join('data', 'ranks.js')

def run():
    ranks = bgpranking.cache_get_top_asns(limit = -1, with_sources = False)
    if ranks.get('top_list') is not None:
        rank_tuples = ranks.get('top_list')
        info = get_country_codes(rank_tuples)
        generate(rank_tuples, info)

def get_country_codes(ranks):
    text_lines = ["begin", "verbose"]
    [text_lines.append("AS" + asn) for asn, rank in ranks]
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

def generate(ranks, info):
    values = {}
    for asn, rank in ranks:
        cc = info[asn]
        if values.get(cc) is None:
            values[cc] = 0
        values[cc] += rank

    f = open(output_file, "w")
    f.write("var ranks =\n" + json.dumps(values))
    f.close()
