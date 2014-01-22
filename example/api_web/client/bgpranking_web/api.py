#!/bin/python
# -*- coding: utf-8 -*-

"""
This is a python implementation to simplify the use of the JSON API.
It allows an access to all the functions of the Redis API, via the network.

The parameters are as consistent as possible with the Redis API.

"""

try:
    import simplejson as json
except:
    import json

import requests

url = 'http://bgpranking.circl.lu/json'

def __prepare_request(query):
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(query), headers=headers)
    return r.json()

def ip_lookup(ip, days_limit = None):
    """See :class:`bgpranking.api.get_ip_info`"""
    query = {'method': 'ip_lookup'}
    query.update({'ip': ip, 'days_limit': days_limit})
    return __prepare_request(query)

def all_ranks_single_asn(asn, last_day = None, timeframe = None,
        dates_sources = None, with_details_sources = None):
    """See :class:`bgpranking.api.get_all_ranks_single_asn`"""
    query = {'method': 'all_ranks_single_asn'}
    query.update({'asn': asn, 'last_day': last_day,
            'timeframe': timeframe, 'dates_sources': dates_sources,
            'with_details_sources': with_details_sources})
    return __prepare_request(query)

def all_ranks_all_asns(last_day = None, timeframe = None,
        dates_sources = None, with_details_sources = None):
    """See :class:`bgpranking.api.get_all_ranks_all_asns`"""
    query = {'method': 'all_ranks_all_asns'}
    query.update({'last_day': last_day, 'timeframe': timeframe,
            'dates_sources': dates_sources,
            'with_details_sources': with_details_sources})
    return __prepare_request(query)

def asn_description(asn, date = None, sources = None):
    """See :class:`bgpranking.api.get_asn_descs`"""
    query = {'method': 'asn_description'}
    if sources is not None and type(sources) is not type([]):
        sources = [sources]
    query.update({'asn': asn, 'date': date, 'sources': sources})
    return __prepare_request(query)

def ips_description(asn, asn_timestamp, date = None, sources = None):
    """See :class:`bgpranking.api.get_ips_descs`"""
    query = {'method': 'ips_description'}
    if sources is not None and type(sources) is not type([]):
        sources = [sources]
    query.update({'asn': asn, 'asn_timestamp': asn_timestamp,
            'date': date, 'sources': sources})
    return __prepare_request(query)

def stats(last_day = None, timeframe = None, dates_sources = None):
    """See :class:`bgpranking.api.get_stats`"""
    query = {'method': 'stats'}
    query.update({'last_day': last_day,'timeframe': timeframe,
            'dates_sources': dates_sources})
    return __prepare_request(query)

def block_descriptions(asn, block):
    """See :class:`bgpranking.api.get_block_descriptions`"""
    query = {'method': 'block_descriptions'}
    query.update({'asn': asn, 'block': block})
    return __prepare_request(query)

def cached_dates():
    """See :class:`bgpranking.api.cache_get_dates`"""
    query = {'method': 'cached_dates'}
    return __prepare_request(query)

def cached_daily_rank(asn, date = None, sources = None):
    """See :class:`bgpranking.api.cache_get_daily_rank`"""
    query = {'method': 'cached_daily_rank'}
    if sources is not None and type(sources) is not type([]):
        sources = [sources]
    query.update({'asn': asn, 'date': date, 'sources': sources})
    return __prepare_request(query)

def cached_top_asns(date = None, source = None, limit = None,
        with_sources = None):
    """See :class:`bgpranking.api.cache_get_top_asns`"""
    query = {'method': 'cached_top_asns'}
    query.update({'date': date, 'source': source, 'limit': limit,
            'with_sources': with_sources})
    return __prepare_request(query)
