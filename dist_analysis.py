#!/usr/bin/env python3
import numpy as np
import numba
from numba import prange
import matplotlib.pyplot as plt
import pickle, tempfile, hashlib
from pathlib import Path

HASH = lambda str: hashlib.sha1(str.encode()).hexdigest()[:6]

@numba.jit(parallel=True)
def _get_pmf_3d(pmf_x1, pmf_x2, y):
    pmf_y = np.zeros(( len(y[0]),len(y[1]) ))
    for x1 in prange(1,len(y[0])):
        for x2 in prange(1,len(y[1])):
            pmf_y[x1,x2] = np.logical_and.reduce((
                y[0]>=pmf_x1[x1-1], y[0]<pmf_x1[x1],
                y[1]>=pmf_x2[x2-1], y[1]<pmf_x2[x2],
            )).sum()
    pmf_y = pmf_y / len(y)
    return pmf_y

def get_pmf_3d(y):
    y = np.array(y).transpose()
    pmf_x1 = np.linspace( 0, np.max(y[0])*1.001, num=len(y[0]) )
    pmf_x2 = np.linspace( 0, np.max(y[1])*1.001, num=len(y[1]) )
    pmf_y  = _get_pmf_3d(pmf_x1, pmf_x2, y)
    return (pmf_x1, pmf_x2, pmf_y)

@numba.jit(parallel=True)
def _get_cdf(y, pmf_x):
    pmf_y = np.zeros(len(y))
    #
    for i in prange(1,len(y)):
        pmf_y[i] = np.logical_and( y>=pmf_x[i-1], y<pmf_x[i] ).sum()
    pmf_y = pmf_y / len(y)
    cdf_y = np.cumsum(pmf_y)
    return pmf_y, cdf_y

def get_pmf_cdf(y):
    pmf_x = np.linspace( 0, np.max(y)*1.001, num=len(y) )
    pmf_y, cdf_y = _get_cdf(y, pmf_x)    
    return (pmf_x, pmf_y, cdf_y)

def defaultAppendFn(ptr, packet):
    if ptr==None:
        return int(packet.length)
    else:
        return (ptr + int(packet.length))
    pass

def Aggregate(packets, limit:float, appendFn, filterFn=None):
    _name = HASH( f'{packets.input_filepath}-{limit}' )
    _name = f'stream-{_name}'
    _file = Path(tempfile.gettempdir()) / _name
    if _file.exists():
        try:
            with open(_file, 'rb') as fp:
                return pickle.load(fp)
        except:
            pass
    ##
    results = list()
    ptr = None
    for idx,packet in enumerate(packets):
        if filterFn and not filterFn(packet):
            # print(f'other packet: {idx}-th.')
            continue
        ##
        _timestamp = float(packet.sniff_timestamp)
        if ptr==None:
            ptr = [_timestamp, appendFn(None, packet)]
        else:
            _key_timestamp = ptr[0]
            if abs(_timestamp-_key_timestamp) <= limit:
                ptr = [ptr[0], appendFn(ptr[1], packet)]
            else:
                results.append(ptr)
                ptr = [_timestamp, appendFn(None, packet)]
        pass
    ##
    with open(_file, 'wb') as fp:
        pickle.dump(results, fp)
    return results

def Analyze3D(y_timeline):
    # x1, x2, pmf = get_pmf_3d(time_length)
    pass

def Analyze(y_timeline, percent, xlabel='', cutoff=None):
    x, pmf, cdf = get_pmf_cdf(y_timeline)

    fig, ax = plt.subplots()
    ##
    x, pmf = np.array(x), np.array(pmf)
    if cutoff:
        _non_zeros = np.where( np.logical_and(pmf>0, x<cutoff) )
    else:
        _non_zeros = np.where( np.logical_and(pmf>0, pmf<1) )
    x = x[_non_zeros]
    pmf = pmf[_non_zeros]; pmf = pmf / sum(pmf)
    # ax.plot( x, pmf, 'bo')

    print( x[ np.array(pmf).argmax() ] )

    sorted_pmf = sorted(pmf,reverse=True)
    _counter = 0
    percent_cnt = list( range(10, 100, 5) )
    cnt = {frac:0 for frac in percent_cnt}
    for i,val in enumerate(sorted_pmf):
        for frac in percent_cnt:
            _frac = frac / 100
            if _counter<_frac and _counter+val >= _frac:
                cnt[frac] = i+1
                print(f'{frac}%: ', i+1)
        _counter += val

    p_x   = x[   np.where(pmf>=sorted_pmf[cnt[percent]]) ]
    p_pmf = pmf[ np.where(pmf>=sorted_pmf[cnt[percent]]) ]
    print(f'Average ({percent}%): ', sum( p_pmf/sum(p_pmf) * p_x ))
    ax.plot( p_x, p_pmf, 'o', color='red')
    #
    if percent<90:
        p_x   = x[   np.where(np.logical_and(pmf>=sorted_pmf[cnt[90]], pmf<sorted_pmf[cnt[percent]])) ]
        p_pmf = pmf[ np.where(np.logical_and(pmf>=sorted_pmf[cnt[90]], pmf<sorted_pmf[cnt[percent]])) ]
        ax.plot( p_x, p_pmf, 'o', color='orange')
    #
    p_x   = x[   np.where(pmf<sorted_pmf[cnt[90]]) ]
    p_pmf = pmf[ np.where(pmf<sorted_pmf[cnt[90]]) ]
    ax.plot( p_x, p_pmf, 'o')

    if percent<90:
        ax.legend([f'<={percent}%', f'({percent}%, 90%]', '>90%'])
    else:
        ax.legend([f'<={percent}%', '>90%'])
    ax.set_ylabel('PMF')
    ax.set_xlabel(xlabel)
    ##
    plt.show()
