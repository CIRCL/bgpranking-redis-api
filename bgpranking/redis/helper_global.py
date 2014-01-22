#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import redis
from dateutil import parser

import constraints as c

__global_db = None
__history_db = None
__config_db = None
__history_db_cache = None

# Tunnel: ssh remote_instance -L 6379:remote_instance:6379

# Default responses
## NOK
__unknown_asn = {'return_code': 0, 'return_vebose': 'Unknown ASN'}
__no_ranks = {'return_code': 0,
            'return_vebose': 'No ranks in this timeframe.'}
__unknown_block = {'return_code': 0,
            'return_vebose': 'Unable to find this IP block.'}
## OK
__ranks = {'return_code': 1, 'return_vebose': 'Got ranks.'}
__owner = {'return_code': 1, 'return_vebose': 'Got owner name.'}

def get_all_weights(date = None):
    """
        Get the weights for all the sources.

        :param date: Date of the information (default: last ranked day)

        :rtype: Dictionary

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        source: date,
                        ...
                    }
    """
    if date is None:
        date = get_default_date()
    sources = daily_sources([date])
    to_return = {}
    if len(sources) > 0:
        impacts = __config_db.mget(sources)
        to_return = dict(zip(sources, impacts))
    return to_return

def daily_sources(dates):
    """
        Get the sources parsed during a list of dates

        :param dates: List of dates

        :rtype: Set of sources for each date

    """
    if len(dates) == 1:
        return __global_db.smembers('{date}|sources'.format(date = dates[0]))
    else:
        p = __global_db.pipeline(False)
        [p.smembers('{date}|sources'.format(date = date)) for date in dates]
        return p.execute()

def prepare_sources_by_dates(last_day = None, timeframe = None):
    """
        Get a dictionary of sources by dates.

        :param last_day: Last day of the interval
        :param timeframe: size of the interval
        :rtype: Dictionary

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        date: [source1, source2, ...],
                        ...
                    }
    """
    dates = __dates_interval(last_day, timeframe)
    sources = daily_sources(dates)
    if len(dates) == 1:
        return {dates[0]: sources}
    return dict(zip(dates, sources))

def get_sources_by_dates(sources, last_day = None, timeframe = None):
    """
        Get a dictionary of sources by dates. Only with the sources passed
        in parameter IF they exist for the day.
        :param sources: List of sources
        :param last_day: Last day of the interval
        :param timeframe: size of the interval

        :rtype: Dictionary

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        date: [source1, source2, ...],
                        ...
                    }


    """
    dates = __dates_interval(last_day, timeframe)
    p = __global_db.pipeline(False)
    for date in dates:
        [p.sismember('{date}|sources'.format(date = date), source)
                for source in sources]
    exists = p.execute()
    i = 0
    to_return = {}
    for date in dates:
        if to_return.get(date) is None:
            to_return[date] = []
        for source in sources:
            if exists[i]:
                to_return[date].append(source)
            i += 1
    return to_return

def last_seen_sources(date_sources):
    """
        Get the last time a source has been seen.
        :param dates_sources: Dictionaries of the dates and sources

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        YYYY-MM-DD: [source1, source2, ...],
                        YYYY-MM-DD: [source1, source2, ...],
                        ...
                    }

        :rype: Dictionary

            .. note:: Format of the dictionary:

                .. code-block:: python

                    {
                        source: date,
                        ...
                    }

    """
    last_seen = {}
    for date in sorted(date_sources.iterkeys(), reverse = True):
        for source in date_sources[date]:
            if last_seen.get(source) is None:
                last_seen[source] = date
    return last_seen

def asn_exists(asn):
    """
        Check if the ASN exists in the database.
    """
    return __global_db.exists(asn)

def get_default_date(delta_days=1):
    """
        Get the latest ranked day.
    """
    return __get_default_date_raw(delta_days).isoformat()

def __prepare():
    global __global_db
    global __history_db
    global __config_db
    global __history_db_cache
    __global_db = redis.Redis(port = c.redis_port, db = c.redis_db_global,
            host = c.redis_hostname)
    __history_db = redis.Redis(port = c.redis_port, db = c.redis_db_history,
            host = c.redis_hostname)
    __config_db = redis.Redis(port = c.redis_port, db = c.redis_db_config,
            host = c.redis_hostname)
    __history_db_cache = redis.Redis(port = c.redis_cached_port,
            db = c.redis_cached_db_history, host = c.redis_hostname)


def __get_default_date_raw(delta_days=1):
    """
        Get the default date displayed on the website.
    """
    delta = datetime.timedelta(days=delta_days)
    try:
        timestamp = __history_db.get('latest_ranking')
    except:
        # TODO: hotfix, can be better
        timestamp = None
    if timestamp is not None:
        default_date_raw = parser.parse(timestamp.split()[0]).date() - delta
    else:
        default_date_raw = datetime.date.today() - delta
    return default_date_raw

def __dates_interval(last_day = None, timeframe = None):
    if last_day is None:
        last_day = __get_default_date_raw()
    else:
        last_day = parser.parse(last_day).date()
    if timeframe is None:
        timeframe = c.default_timeframe
    return [(last_day - datetime.timedelta(days=i)).isoformat()
                    for i in range(timeframe)]
