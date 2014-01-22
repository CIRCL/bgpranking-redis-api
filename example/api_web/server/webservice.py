#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The JSON API allows to do queries on the whole database of BGP Ranking
via the Web interface.

By default, the path where the webservice is listening is
http://domain/json

You need to send a well-formed JSON object with a entry 'method' and as
value the name of the function you want to call (listed bellow).

The other entries of the JSON Object will depend on the function. To keep
it simple, the name of each entry is the parameter name from the Redis API.

The default parameters are as consistent as possible with the one of the
Redis API (:class:`bgpranking.api`)

"""


from flask import Flask, json, request
import StringIO
import csv

import bgpranking_redis as bgpranking
bgpranking.asnhistory.redis_host='127.0.0.1'
bgpranking.asnhistory.redis_port=6389
bgpranking.ipasn.hostname='127.0.0.1'
bgpranking.ipasn.port=6390
bgpranking.ptr_host='127.0.0.1'
bgpranking.ptr_port=8323

logging = True
try:
    if logging:
            from pubsublogger import publisher
            publisher.channel = 'API_Web'
except:
    logging = False


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

def __csv2string(data):
    si = StringIO.StringIO();
    cw = csv.writer(si);
    cw.writerow(data);
    return si.getvalue().strip('\r\n');


def __query_logging(ip, user_agent, method, date=None, source=None,
        asn=None, asn_details=None, compared_asns=None, ip_lookup=None, level=None):
    if level == 'warning':
        publisher.info(__csv2string([ip, user_agent, method, date,
            source, asn, asn_details, compared_asns, ip_lookup]))
    elif level == 'error':
        publisher.info(__csv2string([ip, user_agent, method, date,
            source, asn, asn_details, compared_asns, ip_lookup]))
    else:
        publisher.info(__csv2string([ip, user_agent, method, date,
            source, asn, asn_details, compared_asns, ip_lookup]))


@app.route('/json', methods = ['POST'])
def __entry_point():
    """
        Function called when an query is made on /json. Expects a JSON
        object with at least a 'method' entry.
    """
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', 'Empty User-Agent')
    method = request.json.get('method')
    if method is None:
        __query_logging(ip, ua, method, level = 'warning')
        return json.dumps({'error': 'No method provided.'})
    if method not in authorized_methods:
        # unauthorized query
        __query_logging(ip, ua, method, level = 'warning')
        return json.dumps({'error': 'Unauthorized method.'})
    fct = globals().get(method)
    if fct is None:
        # unknown method, the method is authorized, but does not exists...
        __query_logging(ip, ua, method, level = 'error')
        return json.dumps({'error': 'Unknown method.'})
    try:
        result = fct(request.json)
        __query_logging(ip, ua, method)
        return result
    except:
        __query_logging(ip, ua, method, level = 'error')
        return json.dumps({'error': 'Something went wrong.'})

def ip_lookup(request):
    """See :class:`bgpranking.api.get_ip_info`"""
    ip = request.get('ip')
    if ip is None:
         return json.dumps({})
    return json.dumps(bgpranking.get_ip_info(ip, request.get('days_limit')))

def all_ranks_single_asn(request):
    """See :class:`bgpranking.api.get_all_ranks_single_asn`"""
    asn = request.get('asn')
    if asn is None:
        return json.dumps({})
    dates_sources = __default_dates_sources(request)
    return json.dumps(bgpranking.get_all_ranks_single_asn(asn,
        dates_sources, request.get('with_details_sources')))

def all_ranks_all_asns(request):
    """See :class:`bgpranking.api.get_all_ranks_all_asns`"""
    dates_sources = __default_dates_sources(request)
    with_details_sources = request.get('with_details_sources')
    return json.dumps(bgpranking.get_all_ranks_all_asns(dates_sources,
        with_details_sources))

def block_descriptions(request):
    """See :class:`bgpranking.api.get_block_descriptions`"""
    asn = request.get('asn')
    block = request.get('block')
    if asn is None or block is None:
        return json.dumps([])
    return json.dumps(bgpranking.get_block_descriptions(asn, block))

def asn_description(request):
    """See :class:`bgpranking.api.get_asn_descs`"""
    asn = request.get('asn')
    if asn is None:
        return json.dumps({})
    return json.dumps(bgpranking.get_asn_descs(asn,
        request.get('date'), request.get('sources')))

def ips_description(request):
    """See :class:`bgpranking.api.get_ips_descs`"""
    asn = request.get('asn')
    block = request.get('block')
    if asn is None or block is None:
        return json.dumps({})
    return json.dumps(bgpranking.get_ips_descs(asn, block,
        request.get('date'), request.get('sources')))

def stats(request):
    """See :class:`bgpranking.api.get_stats`"""
    return json.dumps(bgpranking.get_stats(
        __default_dates_sources(request)))


# need cached data
def cached_dates(request):
    """See :class:`bgpranking.api.cache_get_dates`"""
    return json.dumps(bgpranking.cache_get_dates())

def cached_daily_rank(request):
    """See :class:`bgpranking.api.cache_get_daily_rank`"""
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
    """See :class:`bgpranking.api.cache_get_top_asns`"""
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
