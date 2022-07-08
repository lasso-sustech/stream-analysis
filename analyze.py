#!/usr/bin/env python3
import sys, json
import numpy as np
from pyshark import FileCapture
from pathlib import Path
from dist_analysis import Aggregate, Analyze
from dist_analysis import defaultAppendFn

##
try:
    with open('.traces') as f:
        ROOT_FOLDER = Path( f.readlines()[0] ).expanduser()
except:
    ROOT_FOLDER = Path('traces')

##
with open(ROOT_FOLDER/'config.json') as f:
    CONFIG = json.load(f)

##
if len(sys.argv)>1:
    FILE=sys.argv[1]
else:
    _keys = list(CONFIG.keys())
    for i,x in enumerate(_keys):
        print(f'[{i}] {x}')
    _num = int( input('Choice by index: ') )
    FILE = _keys[_num]


##
p = CONFIG[FILE]
_file = (ROOT_FOLDER / FILE).as_posix()
cap = FileCapture(_file, display_filter=p['filter'])
results = Aggregate(cap, limit=p['limit']*1E-3,
        appendFn=defaultAppendFn,
        filterFn=None)

##
_timestamp, _length = zip(*results)
time_delta = np.diff( _timestamp )
_length = np.array(_length[1:])

##
export_filename = (ROOT_FOLDER/FILE).with_suffix('.npy')
_delta_nano = np.array(time_delta) * 1E9
export = np.stack([_delta_nano, _length]).T.astype(np.uint64)
np.save(export_filename, export)

##
if 'interval_percent' in p:
    _cutoff = p['interval_cutoff'] if 'interval_cutoff' in p else 1E9
    Analyze(time_delta, percent=p['interval_percent'], cutoff=_cutoff, xlabel='Video Frame Interval (Second)')

if 'length_percent' in p:
    Analyze(_length, percent=70, xlabel='Video Frame Length (Byte)')
