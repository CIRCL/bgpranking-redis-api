#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    :file:`bin/services/microblog.py` - Microblogging client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Start the microblogging client which posts on twitter and identica
"""

import time
from pubsublogger import publisher
import microblog

dev_mode = True

if __name__ == '__main__':

    sleep_timer = 3600

    publisher.channel = 'Ranking'

    while 1:
        try:
            if microblog.post_new_top_ranking():
                publisher.info('New Ranking posted on twitter and identica.')
        except Exception as e:
            publisher.error("Something bad occurs: " + e.strerror)
        time.sleep(sleep_timer)
