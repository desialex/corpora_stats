import numpy as np
from pprint import pprint

def keyset(dicts):
    """
    Returns the list of all keys and value types
    in a number of dictionaries
    """
    return sorted(set([(k,type(d[k])) for d in dicts for k in d.keys()]))

def normalize_keys(d, keys):
    for k,t in keys:
        if k not in d.keys():
            if str(t) == "<class 'numpy.ndarray'>":
                d[k] = np.array([])
            else:
                d[k] = t()
    return d

def mean_dict(dicts):
    """Takes a list of dicts and returns the average dict"""
    keys = keyset(dicts) # list of keys and types
    dicts = [normalize_keys(d, keys) for d in dicts] # make sure we have the same keys
    mean = {}
    for k,t in keys:
        values = [d[k] for d in dicts]
        if str(t) == "<class 'dict'>":
            mean[k] = mean_dict(values)
        elif str(t) == "<class 'numpy.ndarray'>":
            mean[k] = np.mean(np.concatenate(values))
        else:
            mean[k] = np.mean(np.array(values))
    return mean

d1 = {'a':1, 'b':np.array([1,1]), 'c':{'d':1}, 'f':1, 'h':np.array([0])}
d2 = {'a':3, 'b':np.array([4,4,0]), 'c':{'e':1}, 'g':{}}
dd = [d1,d2]
pprint(mean_dict(dd))
