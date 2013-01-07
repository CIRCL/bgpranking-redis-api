#!/bin/python
# -*- coding: utf-8 -*-

import requests

url = 'http://bgpranking.circl.lu/json_api'

def all_ranks_single_asn(asn, last_day = None, timeframe = None,
        dates_sources = None, with_details_sources = None):
    url = url + '/all_ranks_single_asn'
    payload = {'asn': asn, 'last_day': last_day,
            'timeframe': timeframe, 'dates_sources': dates_sources,
            'with_details_sources': with_details_sources}
    r = requests.post(url, data=payload)
    return r.json

def all_ranks_all_asns(last_day = None, timeframe = None,
        dates_sources = None, with_details_sources = None)
    url = url + '/all_ranks_all_asns'
    payload = {'last_day': last_day, 'timeframe': timeframe,
            'dates_sources': dates_sources,
            'with_details_sources': with_details_sources}
    r = requests.post(url, data=payload)
    return r.json

def asn_description(asn, date = None, sources = None):
    url = url + '/asn_description'
    if sources is not None and type(sources) is not type([]):
        sources = [sources]
    payload = {'asn': asn, 'date': date, 'sources': sources}
    r = requests.post(url, data=payload)
    return r.json

def ips_description(asn, asn_timestamp, date = None, sources = None):
    url = url + '/ips_description'
    if sources is not None and type(sources) is not type([]):
        sources = [sources]
    payload = {'asn': asn, 'asn_timestamp': asn_timestamp,
            'date': date, 'sources': sources}
    r = requests.post(url, data=payload)
    return r.json

def stats(last_day = None, timeframe = None, dates_sources = None):
    url = url + '/stats'
    payload = {'last_day': last_day,'timeframe': timeframe,
            'dates_sources': dates_sources}
    r = requests.post(url, data=payload)
    return r.json

def block_owner_description(asn, block):
    url = url + '/block_owner_description'
    payload = {'asn': asn, 'block': block}
    r = requests.post(url, data=payload)
    return r.json

def cached_dates():
    url = url + '/cached_dates'
    r = requests.post(url)
    return r.json

def cached_daily_rank(asn, date = None, sources = None):
    url = url + '/cached_daily_rank'
    if sources is not None and type(sources) is not type([]):
        sources = [sources]
    payload = {'asn': asn, 'date': date, 'sources': sources}
    r = requests.post(url, data=payload)
    return r.json

def cached_top_asns(date = None, source = None, limit = None,
        with_sources = None):
    url = url + '/cached_top_asns'
    payload = {'date': date, 'source': source, 'limit': limit,
            'with_sources': with_sources}
    r = requests.post(url, data=payload)
    return r.json

