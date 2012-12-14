from flask import Flask, json, request

import bgpranking

app = Flask(__name__)
app.debug = True

@app.route('/all_ranks_single_asn', methods = ['POST'])
def all_ranks_single_asn():
    asn = request.json.get('asn')
    if asn is None:
        return json.dumps({})
    dates_sources = request.json.get('dates_sources')
    if dates_sources is None:
        dates_sources = \
            bgpranking.prepare_sources_by_dates(request.json.get('last_day'),
                    request.json.get('timeframe'))
    with_details_sources = request.json.get('with_details_sources')
    if with_details_sources is None:
        with_details_sources = False
    return json.dumps(bgpranking.get_all_ranks_single_asn(asn,
        dates_sources, with_details_sources))

@app.route('/all_ranks_all_asns', methods = ['POST'])
def all_ranks_all_asns():
    dates_sources = request.json.get('dates_sources')
    if dates_sources is None:
        dates_sources = \
            bgpranking.prepare_sources_by_dates(request.json.get('last_day'),
                    request.json.get('timeframe'))
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

@app.route('/daily_rank', methods = ['POST'])
def daily_rank():
    asn = request.json.get('asn')
    if asn is None:
        return json.dumps({})
    return json.dumps(bgpranking.cache_get_daily_rank(asn,
        request.json.get('sources'), request.json.get('date')))

@app.route('/top_asns', methods = ['POST'])
def top_asns():
    return json.dumps(bgpranking.cache_get_top_asns(request.json.get('source'),
        request.json.get('date'), request.json.get('limit'),
        request.json.get('with_sources')))

if __name__ == '__main__':
    app.run()
