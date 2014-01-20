#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Entry point of the API
"""

import IPy
from dateutil import parser
from dateutil import tz
import datetime

from . import helper_global as h
from . import constraints as c

# Get PTR Record when looking for an IP
get_PTR = True
def get_ptr_record(ip):
    if get_PTR:
        try:
            return h.redis.Redis(host='149.13.33.68', port=8323).get(ip)
        except:
            pass
    return None

try:
    import asnhistory
    use_asnhistory = True
except:
    use_asnhistory = False

try:
    import ipasn.redis as ipasn
    use_ipasn = True
except:
    use_ipasn = False


logging = True
try:
    if logging:
        from pubsublogger import publisher
        publisher.channel = 'API_Redis'
except:
    logging = False

def get_asn_descriptions(asn):
    if not use_asnhistory:
        publisher.debug('ASN History not enabled.')
        return [datetime.date.today(), 'ASN History not enabled.']
    desc_history = asnhistory.get_all_descriptions(asn)
    to_return = []
    for date, descr in desc_history:
        to_return.append([date.astimezone(tz.tzutc()).date(), descr])
    return to_return

def get_ip_info(ip, days_limit = None):
    """
        Return informations related to an IP address.

        :param ip: The IP address
        :param days_limit: The number of days we want to check in the past
            (default: around 2 years)
        :rtype: Dictionary

            .. note:: Format of the output:

                .. code-block:: python

                    {
                        'ip': ip,
                        'days_limit' : days_limit,
                        'history':
                            [
                                {
                                    'asn': asn,
                                    'interval': [first, last],
                                    'block': block,
                                    'timestamp': timestamp,
                                    'descriptions':
                                        [
                                            [date, descr],
                                            ...
                                        ]
                                },
                                ...
                            ]
                    }
    """
    if days_limit is None:
        days_limit = 750
    to_return = {'ip': ip, 'days_limit': days_limit, 'history': [],
            'ptrrecord': get_ptr_record(ip)}
    if not use_ipasn:
        publisher.debug('IPASN not enabled.')
        to_return['error'] = 'IPASN not enabled.'
        return to_return
    if ip is None:
        to_return['error'] = 'No IP provided.'
        return to_return
    for first, last, asn, block in ipasn.aggregate_history(ip, days_limit):
        first_date = parser.parse(first).replace(tzinfo=tz.tzutc()).date()
        last_date = parser.parse(last).replace(tzinfo=tz.tzutc()).date()
        if use_asnhistory:
            desc_history = asnhistory.get_all_descriptions(asn)
            valid_descriptions = []
            for date, descr in desc_history:
                date = date.astimezone(tz.tzutc()).date()
                test_date = date - datetime.timedelta(days=1)
                if last_date < test_date:
                    # Too new
                    continue
                elif last_date >= test_date and first_date <= test_date:
                    # Changes within the interval
                    valid_descriptions.append([date.isoformat(), descr])
                elif first_date > test_date:
                    # get the most recent change befrore the interval
                    valid_descriptions.append([date.isoformat(), descr])
                    break
        else:
            publisher.debug('ASN History not enabled.')
            valid_descriptions = [datetime.date.today().isoformat(),
                    'ASN History not enabled.']
        if len(valid_descriptions) == 0:
            if len(desc_history) != 0:
                # fallback, use the oldest description.
                date = desc_history[-1][0].astimezone(tz.tzutc()).date()
                descr = desc_history[-1][1]
                valid_descriptions.append([date.isoformat(), descr])
            else:
                # No history found for this ASN
                if last_date > datetime.date(2013, 01, 01):
                    # ASN has been seen recently, should not happen
                    # as the asn history module is running since early 2013
                    publisher.error(\
                        'Unable to find the ASN description of {}. IP address: {}. ASN History might be down.'.\
                        format(asn, ip))
                valid_descriptions.append(['0000-00-00',
                    'No ASN description has been found.'])
        entry = {}
        entry['asn'] = asn
        entry['interval'] = [first_date.isoformat(), last_date.isoformat()]
        entry['block'] = block
        entry['timestamp'] = get_first_seen(asn, block)
        entry['descriptions'] = valid_descriptions
        to_return['history'].append(entry)
    return to_return


def get_last_seen_sources(asn, dates_sources):
    """
        Return a dictionary conteining the last date a particular ASN
        has been seen by a source.
    """
    if not h.asn_exists(asn):
        return {}
    string = '{asn}|{date}|{source}|rankv{ip_version}'
    s_dates = dates_sources.keys()
    s_dates.sort(reverse=True)
    p = h.__history_db.pipeline()
    for date in s_dates:
        sources = dates_sources[date]
        if len(sources) > 0:
            [p.exists(string.format(asn=asn, date=date, source=source,
                ip_version = c.ip_version)) for source in sources]
    asns_found = p.execute()
    i = 0
    to_return = {}
    for date in s_dates:
        sources = dates_sources[date]
        if len(sources) > 0:
            for source in sources:
                if to_return.get(source) is None and asns_found[i]:
                    to_return[source] = date
                i += 1
    return to_return

def get_all_ranks_single_asn(asn, dates_sources,
        with_details_sources=False):
    """
        Get all the ranks on a timeframe for a single ASN.

        :param asn: Autonomous System Number
        :param dates_sources: Dictionaries of the dates and sources

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        YYYY-MM-DD: [source1, source2, ...],
                        YYYY-MM-DD: [source1, source2, ...],
                        ...
                    }

        :param with_details_sources: Returns the details by sources if True

        :rype: Dictionary

            .. note:: Format of the output:

                .. code-block:: python

                    {
                        date1:
                            {
                                'details':
                                    [
                                        (source1, rank),
                                        (source2, rank),
                                        ...
                                    ],
                                'total': sum_of_ranks,
                                'description': description
                            }
                        ...
                    }

                The details key is only present if
                ``with_details_sources`` is True.
        """
    to_return = {}
    if with_details_sources is None:
        with_details_sources = False
    if not h.asn_exists(asn):
        return to_return
    string = '{asn}|{date}|{source}|rankv{ip_version}'
    p = h.__history_db.pipeline()
    for date, sources in dates_sources.iteritems():
        if len(sources) > 0:
            p.mget([string.format(asn=asn, date=date, source=source,
                ip_version = c.ip_version) for source in sources])
    ranks = p.execute()
    i = 0
    for date, sources in dates_sources.iteritems():
        impacts = h.get_all_weights(date)
        if len(sources) > 0:
            to_return[date] = {}
            zipped_sources_rank = zip(sources, ranks[i])
            if with_details_sources:
                to_return[date]['details'] = list(zipped_sources_rank)
            to_return[date]['description'] = __asn_desc_via_history(asn)
            to_return[date]['total'] = 0
            for s, r in zipped_sources_rank:
                if r is not None:
                    to_return[date]['total'] += float(r) * float(impacts[s])
            i += 1
    return to_return

def existing_asns_timeframe(dates_sources):
    """
        Get all the ASNs seen in the lists on a timeframe.
    """
    asns_keys = []
    for date, sources in dates_sources.iteritems():
        asns_keys.extend(['{date}|{source}|asns'.format(date = date,
            source = source) for source in sources])
    p = h.__global_db.pipeline(False)
    [p.smembers(k) for k in asns_keys]
    asns_list = p.execute()
    return set.union(*asns_list)

def get_all_ranks_all_asns(dates_sources, with_details_sources = False):
    """
        Get all ranks for all the ASNs on a timeframe.

        :param dates_sources: Dictionaries of the dates and sources

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        YYYY-MM-DD: [source1, source2, ...],
                        YYYY-MM-DD: [source1, source2, ...],
                        ...
                    }

        :param with_details_sources: Also returns the ranks by sources

        :rype: Dictionary

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        YYYY-MM-DD:
                            {
                                asn1 :
                                    {
                                        'details':
                                            [
                                                (source1, rank),
                                                (source2, rank),
                                                ...
                                            ],
                                        'total': sum_of_ranks,
                                        'description': description
                                    }
                                ...
                            }
                        ...
                    }

                The details key is only present if
                ``with_details_sources`` is True.
    """
    asns = existing_asns_timeframe(dates_sources)
    to_return = {}
    for asn in asns:
        details = get_all_ranks_single_asn(asn, dates_sources,
                with_details_sources)
        for date, entries in details.iteritems():
            if to_return.get(date) is None:
                to_return[date] = {}
            to_return[date][asn] = entries
    return to_return

def get_all_blocks(asn):
    """
        Expose the list of blocks announced by an AS.

        :param asn: Autonomous System Number
        :rtype: Set of ip blocks
    """
    return h.__global_db.smembers(asn)

def get_all_blocks_description(asn):
    """
        Get the most recent description of all the blocks announced by an AS

        :param asn: Autonomous System Number
        :rtype: List

            .. note:: Format of the list:

                .. code-block:: python

                    [asn, [(block, description), ...]]
    """
    blocks = get_all_blocks(asn)
    if len(blocks) > 0:
        block_keys = ['{asn}|{block}'.format(asn=asn, block=block)
                for block in blocks]
        p = h.__global_db.pipeline(False)
        for block_key in block_keys:
            p.__global_db.hgetall(block_key)
        ts_descr = p.execute()
        i = 0
        block_descr = []
        for block_key in block_keys:
            if ts_descr[i] is not None:
                asn, block = block_key.split('|')
                most_recent_ts = sorted(ts_descr[i].keys())[0]
                descr = ts_descr[i][most_recent_ts]
                block_descr.append((block, descr))
            i += 1
        return asn, block_descr
    else:
        return asn, []

def get_first_seen(asn, block):
    """
        Get the oldest timestamp where the block has been announced by the AS
    """
    timestamps = h.__global_db.hkeys(asn + '|' + block)
    if timestamps is not None and len(timestamps) > 0:
        timestamps.sort()
        return timestamps[0]
    return None

def get_block_descriptions(asn, block):
    """
        Return all the descriptions of a block, in a listed sorted by
        timestamp (new => old)

        :param asn: Autonomous System Number
        :param block: IP Block you are looking for

        :rtype: List

            .. note:: Format of the list:

                .. code-block:: python

                    [asn, block, [(ts, descr), ...]]
    """
    ts_descr = h.__global_db.hgetall('{}|{}'.format(asn, block))
    timestamps = sorted(ts_descr.keys(), reverse=True)
    descriptions = []
    for t in timestamps:
        descriptions.append((t, ts_descr[t]))
    return asn, block, descriptions

def get_all_blocks_descriptions(asn):
    """
        Return all tuples timestamp-description of all the blocs announced
        by an AS over time.

        :param asn: Autonomous System Number
        :rtype: List

            .. note:: Format of the list:

                .. code-block:: python

                    [   asn,
                        {
                            block:
                                [
                                    (timestamp, description),
                                    ...
                                ],
                            ...
                        }
                    ]
    """
    blocks_descriptions = {}
    for block in get_all_blocks(asn):
        asn, block, descriptions = get_block_descriptions(asn, block)
        blocks_descriptions[block] = descriptions
    return asn, blocks_descriptions

def __asn_desc_via_history(asn):
    if use_asnhistory:
        asn_descr = asnhistory.get_last_description(asn)
        if asn_descr is None:
            # The ASN has no descripion in the database
            #publisher.error(\
            #        'Unable to find the ASN description of {}. ASN History might be down.'.\
            #        format(asn))
            asn_descr = 'No ASN description has been found.'
    else:
        publisher.debug('ASN History not enabled.')
        asn_descr = 'ASN History not enabled.'
    return asn_descr

def get_asn_descs(asn, date = None, sources = None):
    """
        Get all what is available in the database about an ASN for
        one day

        :param asn: Autonomous System Number
        :param date: Date of the information (default: last ranked day)
        :param sources: List of sources (default: the available sources
                        at ``date``)
        :rtype: Dictionary

            .. note:: Format of the dictionary:

                .. code-block:: python

                        {
                            'date': date,
                            'sources': [source1, source2, ...],
                            'asn': asn,
                            'asn_description': asn_description,
                            asn:
                                {
                                    'clean_blocks':
                                        {
                                            block: [[ts, descr], ...],
                                            ....
                                        },
                                    'old_blocks':
                                        {
                                            block: [[ts, descr], ...],
                                            ....
                                        },
                                    block:
                                        {
                                            'description': description,
                                            'timestamp': ts,
                                            'old_descr': [(timestamp, description), ...]
                                            'nb_of_ips': nb,
                                            'sources': [source1, source2, ...]
                                            'rank': subnet_rank
                                        },
                                    ...
                                }
                        }


    """
    if not h.asn_exists(asn):
        # The ASN does not exists in the database
        return None

    if date is None:
        date = h.get_default_date()
    day_sources = h.daily_sources([date])
    if sources is None:
        sources = list(day_sources)
    else:
        if type(sources) is not type([]):
            sources = [sources]
        sources = list(day_sources.intersection(set(sources)))
    asn_descr = __asn_desc_via_history(asn)
    to_return = {'date': date, 'sources': sources, 'asn': asn,
            'asn_description': asn_descr, asn: {}}

    key_clean_set = '{asn}|{date}|clean_set'.format(asn=asn, date=date)
    for ip_block in get_all_blocks(asn):
        # Get descriptions
        asn, block, ts_descr = get_block_descriptions(asn, ip_block)
        # Find out if the block has been seen these day
        p = h.__global_db.pipeline(False)
        [p.scard('{}|{}|{}|{}'.format(asn, ip_block, date, source)) for source in sources]
        ips_by_sources = p.execute()
        nb_of_ips = sum(ips_by_sources)

        if nb_of_ips == 0:
            if ip_block in h.__history_db.smembers(key_clean_set):
                if to_return[asn].get('clean_blocks') is None:
                    to_return[asn]['clean_blocks'] = {}
                to_return[asn]['clean_blocks'][ip_block] = ts_descr
            else:
                if to_return[asn].get('old_blocks') is None:
                    to_return[asn]['old_blocks'] = {}
                to_return[asn]['old_blocks'][ip_block] = ts_descr
        else:
            impacts = h.get_all_weights(date)
            # Compute the local ranking: the ranking if this subnet is
            # the only one for this AS
            i = 0
            sum_rank = 0
            sources_exists = []
            for source in sources:
                sum_rank += float(ips_by_sources[i])*float(impacts[source])
                if ips_by_sources[i] != 0:
                    sources_exists.append(source)
                i += 1
            local_rank = sum_rank / IPy.IP(ip_block).len()
            to_return[asn][ip_block] = {'description': ts_descr[0][1],
                    'timestamp': ts_descr[0][0], 'old_descr': ts_descr[1:],
                    'nb_of_ips': nb_of_ips, 'sources': sources_exists,
                    'rank': local_rank}
    return to_return

def get_ips_descs(asn, block, date = None, sources = None):
    """
        Get all what is available in the database about an subnet for one day

        :param asn: Autonomous System Number
        :param asn_timestamp: First the subnet has been seen in the db
                              (for this ASN)
        :param date: Date of the information (default: last ranked day)
        :param sources: List of sources (default: the available sources
                        at ``date``)

        :rtype: Dictionary

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        'date': date,
                        'sources': [source1, source2, ...],
                        'asn': asn,
                        'asn_description': asn_description,
                        'block': block
                        block:
                            {
                                ip:
                                    {
                                        'sources': [source1, source2, ...],
                                        'ptrrecord': 'ptr.record.com'
                                    }
                                ...
                            }
                    }

    """

    if date is None:
        date = h.get_default_date()
    day_sources = h.daily_sources([date])
    if sources is None:
        sources = list(day_sources)
    else:
        if type(sources) is not type([]):
            sources = [sources]
        sources = list(day_sources.intersection(set(sources)))
    asn_descr = __asn_desc_via_history(asn)
    to_return = {'date': date, 'sources': sources, 'asn': asn,
            'asn_description': asn_descr, 'block': block, block: {}}
    asn_block_key = '{asn}|{b}|{date}|'.format(asn=asn, b=block, date=date)
    pipeline = h.__global_db.pipeline(False)
    [pipeline.smembers('{asn_b}{source}'.format(asn_b=asn_block_key,
                source=source)) for source in sources]
    ips_by_source = pipeline.execute()
    i = 0
    for source in sources:
        ips = ips_by_source[i]
        for ip_details in ips:
            ip, timestamp = ip_details.split('|')
            if to_return[block].get(ip) is None:
                to_return[block][ip] = {'sources': [], 'ptrrecord': None}
            to_return[block][ip]['sources'].append(source)
        i += 1
    for ip in to_return[block]:
        to_return[block][ip]['ptrrecord'] = get_ptr_record(ip)
    return to_return

def get_stats(dates_sources):
    """
        Return amount of asn and subnets found by source on a list of days.

        :param dates_sources: Dictionaries of the dates and sources

        :rtype: Dictionary

            .. note:: Format of the Dictionary

                .. code-block:: python

                    {
                        date:
                            {
                                'sources':
                                    {
                                        source : [nb_asns, nb_subnets],
                                        ...
                                    },
                                'total_asn': total_asn
                                'total_subnets': total_subnets
                            }
                        ...
                    }

    """
    to_return = {}
    p = h.__global_db.pipeline(False)
    for date, sources in dates_sources.iteritems():
        to_return[date] = {}
        for source in sources:
            current_key = '{date}|{source}|asns'.format(date = date,
                    source = source)
            p.scard(current_key)
            p.scard(current_key + '_details')
    cards = p.execute()
    i = 0
    for date, sources in dates_sources.iteritems():
        to_return[date] = {'sources': {}}
        total_asn = 0
        total_subnets = 0
        for source in sources:
            nb_asns = cards[i]
            nb_subnets = cards[i+1]
            total_asn += nb_asns
            total_subnets += nb_subnets
            to_return[date]['sources'].update(
                    {source: (nb_asns, nb_subnets)})
            i = i+2
        to_return[date]['total_asn'] = total_asn
        to_return[date]['total_subnets'] = total_subnets
    return to_return

# Need cached database
def cache_get_dates():
    """
        **From the temporary database**

        Get a list of dates. The ranking are available in the cache database.
    """
    return sorted(h.__history_db_cache.smembers('all_dates'))

def cache_get_stats():
    """
        Return amount of asn and subnets found by source from the cache.
    """
    dates = cache_get_dates()
    dates_sources = dict(zip(dates, h.daily_sources(dates)))
    return get_stats(dates_sources)

def cache_get_daily_rank(asn, source = 'global', date = None):
    """
        **From the temporary database**

        Get a single rank.

        :param asn: Autonomous System Number
        :param source: Source to use. global is the aggregated view for
                       all the sources
        :param date: Date of the information (default: last ranked day)

        :rtype: List

            .. note:: Format of the list

                .. code-block:: python

                    [asn, asn_description, date, source, rank]
    """
    if source is None:
        source = 'global'
    if date is None:
        date = h.get_default_date()
    histo_key = '{date}|{source}|rankv{ip_version}'.format(
            date = date, source = source, ip_version = c.ip_version)
    asn_descr = __asn_desc_via_history(asn)
    return asn, asn_descr, date, source, h.__history_db_cache.zscore(histo_key, asn)

def cache_get_position(asn, source = 'global', date = None):
    """
        **From the temporary database**

        Get the position of the ASN in the zrank.

        :param asn: Autonomous System Number
        :param source: Source to use. global is the aggregated view for
                       all the sources
        :param date: Date of the information (default: last ranked day)

        :rtype: Integer, position in the list and size of the list.

            .. note:: if None, the zrank does not exists (source or date invalid)
    """
    if source is None:
        source = 'global'
    if date is None:
        date = h.get_default_date()
    histo_key = '{date}|{source}|rankv{ip_version}'.format(
            date = date, source = source, ip_version = c.ip_version)
    return h.__history_db_cache.zrevrank(histo_key, asn), \
            h.__history_db_cache.zcard(histo_key)


def cache_get_top_asns(source = 'global', date = None, limit = 100,
        with_sources = True):
    """
        **From the temporary database**

        Get worse ASNs.

        :param source: Source used to rank the ASNs. global is the
                       aggregated view for all the sources
        :param date: Date of the information (default: last ranked day)
        :param limit: Number of ASNs to get
        :param with_sources: Get the list of sources where each ASN has
                             been found.

        :rtype: Dictionary

            .. note:: Format of the Dictionary

                .. code-block:: python

                    {
                        'source': source,
                        'date': date,
                        'size_list': size,
                        'top_list':
                            [
                                (
                                    (asn, asn_description, rank),
                                    set([source1, source2, ...])
                                ),
                                ...
                            ]
                    }

                The set of sources is only presetn if ``with_sources``
                is True

    """
    if source is None:
        source = 'global'
    if date is None:
        date = h.get_default_date()
    if limit is None:
        limit = 100
    if with_sources is None:
        with_sources = True
    histo_key = '{date}|{histo_key}|rankv{ip_version}'.format(date = date,
                       histo_key = source, ip_version = c.ip_version)
    to_return = {'source': source, 'date': date,
            'size_list': h.__history_db_cache.zcard(histo_key), 'top_list': []}
    ranks = h.__history_db_cache.zrevrange(histo_key, 0, limit, True)
    if ranks is None:
        return to_return
    temp_rank = []
    for asn, rank in ranks:
        if asn == '-1':
            continue
        asn_descr = __asn_desc_via_history(asn)
        temp_rank.append((asn, asn_descr, rank))
    if not with_sources:
        to_return['top_list'] = temp_rank
    else:
        p = h.__history_db_cache.pipeline(False)
        [p.smembers('{}|{}'.format(date, rank[0])) for rank in temp_rank]
        to_return['top_list'] = list(zip(temp_rank, p.execute()))
    return to_return

