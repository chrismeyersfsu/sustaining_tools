#!/usr/bin/env python

import os
import re
from datetime import datetime


fpath = os.getenv('DAPHNE_FILE')

log = open(fpath).readlines()

# [09/Sep/2021:19:49:20] "WSCONNECT
p = re.compile('\[(.*)\] "WSCONNECT')

connection_events = []

for l in log:
    m = p.search(l)
    if m:
        datetime_str = m.group(1)
        res = datetime.strptime(datetime_str, '%d/%b/%Y:%H:%M:%S')
        connection_events.append(res)

for e in connection_events:
    s = (e - datetime(1970,1,1)).total_seconds()
    print(s)

