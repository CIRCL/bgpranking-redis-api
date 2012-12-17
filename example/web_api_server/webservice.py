from flask import Flask, json, request

import bgpranking

app = Flask(__name__)
app.debug = True

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

@app.route('/all_ranks_single_asn', methods = ['POST'])
def all_ranks_single_asn():
    asn = request.json.get('asn')
    if asn is None:
        return json.dumps({})
    dates_sources = __default_dates_sources(request.json)
    with_details_sources = request.json.get('with_details_sources')
    if with_details_sources is None:
        with_details_sources = False
    return json.dumps(bgpranking.get_all_ranks_single_asn(asn,
        dates_sources, with_details_sources))

@app.route('/all_ranks_all_asns', methods = ['POST'])
def all_ranks_all_asns():
    dates_sources = __default_dates_sources(request.json)
    with_details_sources = request.json.get('with_details_sources')
    return json.dumps(bgpranking.get_all_ranks_all_asns(dates_sources,
        with_details_sources))

@app.route('/asn_description', methods = ['POST'])
def asn_description():
    asn = request.json.get('asn')
    if asn is None:
        return json.dumps({})
    return json.dumps(bgpranking.get_asn_descs(asn, request.json.get('date'),
        request.json.get('sources')))

@app.route('/ips_description', methods = ['POST'])
def ips_description():
    asn = request.json.get('asn')
    asn_timestamp = request.json.get('asn_timestamp')
    if asn is None or asn_timestamp is None:
        return json.dumps({})
    return json.dumps(bgpranking.get_ips_descs(asn, asn_timestamp,
        request.json.get('date'), request.json.get('sources')))

@app.route('/stats', methods = ['POST'])
def stats():
    return json.dumps(bgpranking.get_stats(__default_dates_sources(request.json)))

@app.route('/block_owner_description', methods = ['POST'])
def block_owner_description():
    asn = request.json.get('asn')
    block = request.json.get('block')
    if asn is None or block is None:
        return json.dumps([])
    return json.dumps(bgpranking.get_owner(asn, block))

# need cached data
@app.route('/cached_dates', methods = ['POST'])
def cached_dates():
    return json.dumps(bgpranking.cache_get_dates())

@app.route('/daily_rank', methods = ['POST'])
def daily_rank():
    asn = request.json.get('asn')
    if asn is None:
        return json.dumps({})
    cached_dates = bgpranking.cache_get_dates()
    date = request.json.get('date')
    if date is None or date in cached_dates:
        return json.dumps(bgpranking.cache_get_daily_rank(asn,
            request.json.get('sources'), date))
    return json.dumps({})

@app.route('/top_asns', methods = ['POST'])
def top_asns():
    cached_dates = bgpranking.cache_get_dates()
    date = request.json.get('date')
    if date is None or date in cached_dates:
        return json.dumps(bgpranking.cache_get_top_asns(request.json.get('source'),
            date, request.json.get('limit'), request.json.get('with_sources')),
            cls=SetEncoder)
    return json.dumps({})


if __name__ == '__main__':
    app.run()
