#!/bin/bash

log_subscriber --mail ./mail.conf --channel Website --log_path ./logs/ &
log_subscriber --mail ./mail.conf --channel API_Twitter --log_path ./logs/ &
log_subscriber --mail ./mail.conf --channel API_Redis --log_path ./logs/ &
log_subscriber --mail ./mail.conf --channel API_Web --log_path ./logs/ &
