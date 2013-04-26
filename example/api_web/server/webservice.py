#!/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, json, request

import bgpranking

app = Flask(__name__)
app.debug = True

authorized_methods = ['all_ranks_single_asn', 'all_ranks_all_asns',
        'block_descriptions', 'asn_description', 'ips_description',
        'stats', 'cached_dates', 'cached_daily_rank', 'cached_top_asns',
        'ip_lookup']

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) == type(set()):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

def __default_dates_sources(req):
    dates_sources = req.get('dates_sources')
    if dates_sources is None:
         dates_sources = \
                 bgpranking.prepare_sources_by_dates(req.get('last_day'),
                         req.get('timeframe'))
    return dates_sources

@app.route('/json', methods = ['POST'])
def entry_point():
    method = request.json.get('method')
    if method is None:
        # wrong query
        return json.dumps({})
    if method not in authorized_methods:
        # unauthorized query
        return json.dumps({})
    fct = globals().get(method)
    if fct is None:
        # unknown method
        return json.dumps({})
    return fct(request.json)

def ip_lookup(request):
    ip = request.get('ip')
    if ip is None:
         return json.dumps({})
    return json.dumps(bgpranking.get_ip_info(ip, request.get('days_limit')))

def all_ranks_single_asn(request):
    asn = request.get('asn')
    if asn is None:
        return json.dumps({})
    dates_sources = __default_dates_sources(request)
    return json.dumps(bgpranking.get_all_ranks_single_asn(asn,
        dates_sources, request.get('with_details_sources')))

def all_ranks_all_asns(request):
    dates_sources = __default_dates_sources(request)
    with_details_sources = request.get('with_details_sources')
    return json.dumps(bgpranking.get_all_ranks_all_asns(dates_sources,
        with_details_sources))

def block_descriptions(request):
    asn = request.get('asn')
    block = request.get('block')
    if asn is None or block is None:
        return json.dumps([])
    return json.dumps(bgpranking.get_block_descriptions(asn, block))

def asn_description(request):
    asn = request.get('asn')
    if asn is None:
        return json.dumps({})
    return json.dumps(bgpranking.get_asn_descs(asn,
        request.get('date'), request.get('sources')))

def ips_description(request):
    asn = request.get('asn')
    block = request.get('block')
    if asn is None or block is None:
        return json.dumps({})
    return json.dumps(bgpranking.get_ips_descs(asn, block,
        request.get('date'), request.get('sources')))

def stats(request):
    return json.dumps(bgpranking.get_stats(
        __default_dates_sources(request)))


# need cached data
def cached_dates(request):
    return json.dumps(bgpranking.cache_get_dates())

def cached_daily_rank(request):
    asn = request.get('asn')
    if asn is None:
        return json.dumps({})
    cached_dates = bgpranking.cache_get_dates()
    date = request.get('date')
    if date is None or date in cached_dates:
        return json.dumps(bgpranking.cache_get_daily_rank(asn,
            request.get('sources'), date))
    return json.dumps({})

def cached_top_asns(request):
    cached_dates = bgpranking.cache_get_dates()
    date = request.get('date')
    if date is None or date in cached_dates:
        return json.dumps(bgpranking.cache_get_top_asns(
            request.get('source'), date, request.get('limit'),
            request.get('with_sources')),
            cls=SetEncoder)
    return json.dumps({})


if __name__ == '__main__':
    app.run()
