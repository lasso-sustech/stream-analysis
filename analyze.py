#!/usr/bin/env python3
from time import time
import numpy as np
from pyshark import FileCapture
import matplotlib.pyplot as plt
from dist_analysis import Aggregate, Analyze
from dist_analysis import defaultAppendFn
import scipy.io

PORT_VIDEO = 35505#42641 #for tx side
PORT_CTRL  = 0#64858 #for tx side

CONFIG = {
    'lap2tv.pcapng': {
        'filter': 'udp.srcport==55501',
        'limit': 1.3,#ms
        'interval_cutoff': 0.1,
        'interval_percent': 15,
        'length_percent': 90,
    },
    'huawei-video.pcapng': {
        'filter': 'tcp.srcport==42641',
        'limit':  3.65,#ms
        'interval_cutoff': 70E-3,
        'interval_percent': 75,
        'length_percent': 90,
    },
    'h2h.pcapng': {
        'filter': 'tcp.srcport==38255 or tcp.srcport==42871',
        'limit':  4.9,#ms
        'interval_cutoff': 70E-3,
        'interval_percent': 75,
        'length_percent': 70,
    }
}

FILE = 'lap2tv.pcapng'

p = CONFIG[FILE]
cap = FileCapture(f'traces/{FILE}', display_filter=p['filter'])

# _filter = f'ip.addr==192.168.137.1 and (tcp.port=={PORT_VIDEO} or tcp.port=={PORT_CTRL})'
# video_stream = {'tx':[], 'rx':[]}
# ctrl_stream  = {'tx':[], 'rx':[]}
# for packet in cap:
#     _tcp = packet.tcp
#     ##
#     if _tcp.srcport==str(PORT_VIDEO):
#         video_stream['tx'].append(packet)
#     elif _tcp.dstport==str(PORT_VIDEO):
#         video_stream['rx'].append(packet)
#     elif _tcp.srcport==str(PORT_CTRL):
#         ctrl_stream['tx'].append(packet)
#     elif _tcp.dstport==str(PORT_CTRL):
#         ctrl_stream['rx'].append(packet)
#     else:
#         raise Exception('display filter is wrong.')

results = Aggregate(cap, limit=p['limit']*1E-3,
        appendFn=defaultAppendFn,
        filterFn=None)

# _timestamp, _length = zip(*results)
# scipy.io.savemat('h2h_16ms.mat', {
#     'timestamp': _timestamp,
#     'length': _length
# })


_timestamp, _length = zip(*results)
time_delta = np.diff( _timestamp )
_length = np.array(_length[1:])

# fig, ax = plt.subplots()
# ax.plot(time_delta)
# ax.set_xlabel('Sequence Number')
# ax.set_ylabel('Packet Interval (Second)')
# plt.show()

if p['interval_percent']:
    _cutoff = p['interval_cutoff'] if 'interval_cutoff' in p else 1E9
    Analyze(time_delta, percent=p['interval_percent'], cutoff=_cutoff, xlabel='Video Frame Interval (Second)')

if p['length_percent']:
    Analyze(_length, percent=70, xlabel='Video Frame Length (Byte)')
