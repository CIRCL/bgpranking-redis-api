#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Entry point of the API
"""

import IPy
#import datetime

from . import helper_global as h
from . import constraints as c

__owner_cache = {}

def get_daily_rank_multiple_asns(asns, date, source):
    """
        Get the ranks of a list of ASNs for one day and one source.

        :param asns: list of ASNs
        :param date: date of the rank (format: YYYY-MM-DD)
        :param source: name of the source for the rank


        :rtype: list of rank by ASN

            .. note:: Format of the output:

                .. code-block:: python

                    [
                        (asn1, rank),
                        (asn2, rank),
                        ...
                    ]
    """
    string = '|{date}|{source}|rankv{ip_version}'.format(date = date,
                source = source, ip_version = c.ip_version)
    to_get = ['{asn}{string}'.format(asn = asn, string = string)
            for asn in asns]
    if len(to_get) == 0:
        return []
    return list(zip(asns, h.__history_db.mget(to_get)))

def get_all_ranks_single_asn(asn, dates_sources, with_details_sources=False):
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
                                'total': sum_of_ranks
                            }
                        ...
                    }

                The details key is only present if ``with_details_sources``
                is True.
    """
    to_return = {}
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
            if with_details_sources:
                to_return[date].update({'details': list(zip(sources, ranks[i]))})
            to_return[date].update({'total' : 0})
            for s, r in zip(sources, ranks[i]):
                if r is not None:
                    to_return[date]['total'] += float(r) * float(impacts[s])
            i += 1
    return to_return

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
                                        'total': sum_of_ranks
                                    }
                                ...
                            }
                        ...
                    }

                The details key is only present if ``with_details_sources``
                is True.
    """
    asns_keys = []
    # prepare the keys to get all the asns by date and source
    for date, sources in dates_sources.iteritems():
        asns_keys.extend(['{date}|{source}|asns'.format(date = date,
            source = source) for source in sources])
    # get it
    p = h.__global_db.pipeline(False)
    [p.smembers(k) for k in asns_keys]
    asns_list = p.execute()
    asns = set.union(*asns_list)
    to_return = {}
    for asn in asns:
        details = get_all_ranks_single_asn(asn, dates_sources,
                with_details_sources)
        for date, entries in details.iteritems():
            if to_return.get(date) is None:
                to_return[date] = {}
            to_return[date][asn] = entries
    return to_return

def get_owner(asn, block):
    """
        Get the description of the ASN (usually the owner name).

        :param asn: Autonomous System Number
        :param block: IP Block you are looking for
        :rtype: List

            .. note:: Format of the list:

                .. code-block:: python

                    [asn, block, owner]

    """
    global __owner_cache
    if __owner_cache.get(asn) is None:
        if not h.asn_exists(asn):
            return h.unknown_asn
        timestamps = h.__global_db.smembers(asn)
        t_keys = [ '{asn}|{t}|ips_block'.format(asn = asn, t = t)
                for t in timestamps]
        temp_blocks = h.__global_db.mget(t_keys)
        __owner_cache[asn] = list(zip(timestamps, temp_blocks))
    owner = None
    for ts, temp_block in __owner_cache[asn]:
        if temp_block==block:
            owner = h.__global_db.get('{asn}|{t}|owner'.format(asn = asn,
                t = ts))
            break
    return [asn, block, owner]


def get_asn_descs(asn, date = None, sources = None):
    """
        Get all what is available in the database about an ASN for one day

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
                            asn:
                                {
                                    'clean_blocks':
                                        [
                                            (timestamp, block, descr),
                                            ...
                                        ],
                                    'old_blocks':
                                        [
                                            (timestamp, block, descr),
                                            ...
                                        ],
                                    asn_timestamp:
                                        {
                                            'owner': owner_description,
                                            'ip_block': block,
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
        sources = list(day_sources.intersection(set(sources)))
    to_return = {'date': date, 'sources': sources, 'asn': asn, asn: {}}
    for timestamp in h.__global_db.smembers(asn):
        # Get the number of IPs found in the database for each subnet
        asn_timestamp_key = '{asn}|{timestamp}|'.format(asn = asn,
                                timestamp = timestamp)
        p = h.__global_db.pipeline(False)
        [p.scard('{asn_ts}{date}|{source}'.format(asn_ts=asn_timestamp_key,
            date = date, source=source)) for source in sources]
        ips_by_sources = p.execute()
        nb_of_ips = sum(ips_by_sources)

        key_owner = '{asn_ts}owner'.format(asn_ts = asn_timestamp_key)
        key_block = '{asn_ts}ips_block'.format(asn_ts = asn_timestamp_key)
        key_clean_set = '{asn}|{date}|clean_set'.format(asn = asn, date = date)
        owner, ip_block = h.__global_db.mget([key_owner, key_block])
        if nb_of_ips > 0:
            impacts = h.get_all_weights(date)
            # Compute the local ranking: the ranking if this subnet is the
            # only one for this AS
            i = 0
            sum_rank = 0
            sources_exists = []
            for source in sources:
                sum_rank += float(ips_by_sources[i])*float(impacts[source])
                if ips_by_sources[i] != 0:
                    sources_exists.append(source)
                i += 1
            local_rank = sum_rank / IPy.IP(ip_block).len()
            to_return[asn][timestamp] = {'owner': owner,
                    'ip_block': ip_block, 'nb_of_ips': nb_of_ips,
                    'sources': sources_exists, 'rank': local_rank}
        elif ip_block in h.__history_db.smembers(key_clean_set):
            if to_return[asn].get('clean_blocks') is None:
                to_return[asn]['clean_blocks'] = []
            to_return[asn]['clean_blocks'].append(
                    (timestamp, ip_block, owner))
        else:
            # Not announced anymore.
            if to_return[asn].get('old_blocks') is None:
                to_return[asn]['old_blocks'] = []
            to_return[asn]['old_blocks'].append(
                    (timestamp, ip_block, owner))
    return to_return

def get_ips_descs(asn, asn_timestamp, date = None, sources = None):
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
                        'timestamp': asn_timestamp
                        asn_timestamp:
                            {
                                ip: [source1, source2, ...],
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
        sources = list(day_sources.intersection(set(sources)))

    asn_timestamp_key = '{asn}|{timestamp}|{date}|'.format(asn = asn,
                    timestamp = asn_timestamp, date = date)
    pipeline = h.__global_db.pipeline(False)
    [pipeline.smembers('{asn_ts}{source}'.format(
                asn_ts = asn_timestamp_key, source=source))
                for source in sources]
    ips_by_source = pipeline.execute()
    i = 0
    to_return = {'date': date, 'sources': sources, 'asn': asn,
            'timestamp': asn_timestamp, asn_timestamp: {}}
    for source in sources:
        ips = ips_by_source[i]
        for ip_details in ips:
            ip, timestamp = ip_details.split('|')
            if to_return[asn_timestamp].get(ip) is None:
                to_return[asn_timestamp][ip] = [source]
            else:
                to_return[asn_timestamp][ip].append(source)
        i += 1
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

                    [asn, date, source, rank]
    """
    if date is None:
        date = h.get_default_date()
    histo_key = '{date}|{source}|rankv{ip_version}'.format(
            date = date, source = source, ip_version = c.ip_version)
    return asn, date, source, h.__history_db_cache.zscore(histo_key, asn)

def cache_get_top_asns(source = 'global', date = None, limit = 50,
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
                        'top_list':
                            [
                                ((asn, rank), set([source1, source2, ...])),
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
    histo_key = '{date}|{histo_key}|rankv{ip_version}'.format(date = date,
                       histo_key = source, ip_version = c.ip_version)
    to_return = {'source': source, 'date': date, 'top_list': []}
    ranks = h.__history_db_cache.zrevrange(histo_key, 0, limit, True)
    if ranks is None:
        return to_return
    if not with_sources:
        to_return['top_list'] = ranks
    else:
        p = h.__history_db_cache.pipeline(False)
        [p.smembers('|'.join([date, rank[0]])) for rank in ranks]
        to_return['top_list'] = list(zip(ranks, p.execute()))
    return to_return

