#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
    Micro-blog
    ~~~~~~~~~~

    Microblog client for twitter

"""

import tweepy

from micro_blog_keys import *
import bgpranking

api = None
auth = None

def __prepare():
    global api
    global auth
    auth = tweepy.OAuthHandler(twitter_consumer_key,
            twitter_consumer_secret)
    auth.set_access_token(twitter_access_key, twitter_access_secret)
    api = tweepy.API(auth)

class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.text.startswith('@bgpranking AS'):
            asn = status.text.strip('@bgpranking AS')
            msg_id = status.id
            sender = status.user.screen_name
            dates_sources = bgpranking.prepare_sources_by_dates(timeframe=5)
            ranks = bgpranking.get_all_ranks_single_asn(asn, dates_sources)
            to_post = '@{user}: {asn}\n'.format(user=sender, asn=asn)
            for date, info in ranks.iteritems():
                to_post += date + ': ' + round(1+info['total'], 4) + '\n'
            to_post += 'http://bgpranking.circl.lu/asn_details?asn=' + asn
            api.update_status(to_post, msg_id)
        else:
            print status.text

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream


def stream_mentions():
    options = {'secure':True}
    listener = CustomStreamListener()
    s = tweepy.streaming.Stream(auth, listener, **options)
    s.userstream()

if __name__ == '__main__':
    stream_mentions()
