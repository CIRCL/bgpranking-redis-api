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
        return [(rank[0], 1 + rank[1], ', '.join(sources))
                for rank, sources in response['top_list']]

def get_sources(date):
    if date is None:
        date = bgpranking.get_default_date()
    return bgpranking.daily_sources([date])

def get_dates():
    return bgpranking.cache_get_dates()

def get_last_month_sources():
    dates_sources = bgpranking.prepare_sources_by_dates(timeframe = 30)
    return bgpranking.last_seen_sources(dates_sources)

def get_as_infos(asn, date = None, sources = None):
    response = bgpranking.get_asn_descs(asn, date, sources)
    if response is None or response.get(asn) is None:
        return None
    to_return = []
    for key, entry in response[asn].iteritems():
        if key == 'clean_blocks':
            pass
        elif key == 'old_blocks':
            pass
        else:
            to_return.append([key, entry['owner'], entry['ip_block'],
                entry['nb_of_ips'], ', '.join(entry['sources']),
                1 + entry['rank']])
    return sorted(to_return, key=lambda element: (element[5], element[3]), reverse = True)

def get_ip_info(asn, timestamp, date = None, sources = None):
    response = bgpranking.get_ips_descs(asn, timestamp, date, sources)
    if response.get(timestamp) is None:
        return None
    to_return = [(ip, ', '.join(sources))
            for ip, sources in response[timestamp].iteritems()]
    return sorted(to_return, key=lambda element: len(element[1]), reverse = True)
