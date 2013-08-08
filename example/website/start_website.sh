#!/bin/bash

log_subscriber --channel Website --log_path ./logs/ &

python master.py
