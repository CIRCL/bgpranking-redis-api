# -*- coding: utf-8 -*-
"""
    Controler class of the website
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The website respects the MVC design pattern and this class is the controler.
    It gets the datas from the `report` class.

"""

import bgpranking

def prepare_index(source, date, limit=50):
    response = bgpranking.cache_get_top_asns(source, date, limit)
    if len(response['top_list']) != 0:
        return [(rank[0], rank[1], 1 + rank[2], ', '.join(sources))
                    for rank, sources in response['top_list']], \
                response['size_list']

def get_sources(date):
    if date is None:
        date = bgpranking.get_default_date()
    return bgpranking.daily_sources([date])

def get_dates():
    return bgpranking.cache_get_dates()

def get_asn_descriptions(asn):
    return bgpranking.get_asn_descriptions(asn)

def get_last_seen_sources(asn):
    dates_sources = bgpranking.prepare_sources_by_dates(timeframe = 365)
    return bgpranking.get_last_seen_sources(asn, dates_sources)

def get_comparator_metatada(asns_string):
    splitted_asns = asns_string.split()
    if type(splitted_asns) == type(str):
        splitted_asns = [splitted_asns]
    details_list = []
    for asn in splitted_asns:
        details_list.append(bgpranking.get_all_blocks_descriptions(asn))
    return splitted_asns, details_list

def get_as_infos(asn, date = None, sources = None):
    response = bgpranking.get_asn_descs(asn, date, sources)
    if response is None or response.get(asn) is None:
        return None, None
    to_return = []
    for key, entry in response[asn].iteritems():
        if key == 'clean_blocks':
            to_return += [[descr[0][1], block, 0, '', 0]
                    for block, descr in entry.iteritems()]
        elif key == 'old_blocks':
            pass
        else:
            to_return.append([entry['description'], key, entry['nb_of_ips'],
                ', '.join(entry['sources']), 1 + entry['rank']])
    return response['asn_description'], sorted(to_return,
            key=lambda element: (element[4], element[2]), reverse = True)

def get_ip_info(asn, block, date = None, sources = None):
    response = bgpranking.get_ips_descs(asn, block, date, sources)
    if response.get(block) is None:
        return None
    to_return = [(ip, ', '.join(sources))
            for ip, sources in response[block].iteritems()]
    return sorted(to_return, key=lambda element: len(element[1]),
            reverse=True)

def get_ip_lookup(ip):
    response = bgpranking.get_ip_info(ip)
    if len(response.get('history')) == 0:
        return None
    return response.get('history')
