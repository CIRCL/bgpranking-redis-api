#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
    Micro-blog
    ~~~~~~~~~~

    Microblog client for twitter

"""

import tweepy
import IPy

from micro_blog_keys import *
import bgpranking

api = None
auth = None
base_asn_address = 'http://bgpranking.circl.lu/asn_details?asn='

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
            try:
                int(asn)
            except:
                print status.text
                return
            msg_id = status.id
            sender = status.user.screen_name
            dates_sources = bgpranking.prepare_sources_by_dates(timeframe=5)
            ranks = bgpranking.get_all_ranks_single_asn(asn, dates_sources)
            to_post = '@{user}: {asn}\n'.format(user=sender, asn=asn)
            dates = sorted(ranks.keys(), reverse=True)
            for date in dates:
                info = ranks[date]
                to_post += '{date}: {rank}\n'.format(date=date,rank=round(1+info['total'], 4))
            to_post += base_asn_address + asn
            api.update_status(to_post, msg_id)
        elif status.text.startswith('@bgpranking IP'):
            ip = status.text.strip('@bgpranking IP')
            try:
                IPy.IP(ip)
            except:
                print status.text
                return
            msg_id = status.id
            sender = status.user.screen_name
            info = bgpranking.get_ip_info(ip, 10)
            to_post_short = '@{user}: {ip}: http://bgpranking.circl.lu/ip_lookup?ip={ip}'.format(user=sender, ip=ip)
            if len(info['history']) > 0:
                latest_data = info['history'][0]
                template = '\n{asn} - {block}: {base_asn_url}{asn};ip_details={block}\n{descr}'
                descr = latest_data['descriptions'][0][1]
                if len(descr) > 40:
                    descr = 'Too Long for Twitter.'
                to_post = to_post_short + template.format(asn=latest_data['asn'],
                        base_asn_url=base_asn_address,
                        block=latest_data['block'], descr=descr)
            try:
                api.update_status(to_post, msg_id)
            except:
                api.update_status(to_post_short, msg_id)

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
    __prepare()
    stream_mentions()
