#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
    Micro-blog
    ~~~~~~~~~~

    Microblog client for twitter

"""

import twitter
import datetime

from micro_blog_keys import *
import bgpranking

api = None
username = "bgpranking"

def __prepare():
    global api
    api = twitter.Api(consumer_key=twitter_customer_key,
            consumer_secret=twitter_consumer_secret,
            access_token_key=twitter_access_token_key,
            access_token_secret=twitter_access_token_secret)

def prepare_string():
    to_return = 'Top Ranking {date}\n'.format(
            date=datetime.date.today().isoformat())
    top = bgpranking.cache_get_top_asns(limit=5, with_sources=False)
    for asn, descr, rank in top['top_list']:
        to_return += '{asn}: {rank}\n'.format(asn=asn, rank=rank)
    to_return += 'http://bgpranking.circl.lu'
    return to_return


def post_new_top_ranking():
    found = False
    posted = False
    today = datetime.date.today()
    i = 1
    while not found:
        if i>= 20:
            break
        status = api.GetUserTimeline("bgpranking", page=i)
        i += 1
        for s in status:
            t = s.get('text')
            if t is not None and t.startswith('Top Ranking'):
                found = True
                most_recent_post = dateutil.parser.parse(
                        s.get('created_at')).replace(tzinfo=None)
                if most_recent_post < today:
                    posted = True
                    to_post = prepare_string()
                    api.PostUpdate(to_post)
    return posted
