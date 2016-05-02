#!/usr/bin/python
# -*- coding: utf-8 -*-

ip_version = 4
# How any days in the past do we want
default_timeframe = 3

# Redis Config
redis_hostname1 = '127.0.0.1'
redis_port1 = 6379
redis_db_global = 5
redis_db_history = 6
redis_db_config = 7
redis_hostname2 = '127.0.0.1'
redis_port2 = 6479
# Redis Cached
redis_cached_port = 6382
redis_cached_db_history = 6
# PTR records DB
ptr_host = '127.0.0.1'
ptr_port = 8323
# ASN history
asn_host = '127.0.0.1'
asn_port = 6389
# IP ASN
ipasn_host = '127.0.0.1'
ipasn_port = 16379

# Archive config
last_year_archived = 2015
archive_host = '127.0.0.1'
archive_port = 6399
