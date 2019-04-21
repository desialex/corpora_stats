import numpy as np
from pprint import pprint

def keyset(dicts):
    """
    Returns the list of all keys and value types in a list of dictionaries
    """
    return sorted(set([(k,type(d[k])) for d in dicts for k in d.keys()]))

def normalize_keys(d, keys):
    for k,t in keys:
        if k not in d.keys():
            d[k] = t()
    return d

def mean_dict(dicts):
    """
    Takes a list of dicts and returns a dict with mean values
    Assuming values are int/float or dict
    """
    keys = keyset(dicts) # list of keys and types
    dicts = [normalize_keys(d, keys) for d in dicts] # make sure we have the same keys
    mean = {}
    for k,t in keys:
        values = [d[k] for d in dicts]
        if str(t) == "<class 'dict'>":
            mean[k] = mean_dict(values)
        else:
            mean[k] = np.mean(values)
    return mean

def normalize_dicts(dicts):
    """Normalize the values across a list of dictionaries (offset and scale)"""
    keys = keyset(dicts) # list of keys and types
    dicts = [normalize_keys(d, keys) for d in dicts] # make sure we have the same keys
    for k,t in keys:
        if str(t) == "<class 'dict'>":
            values = [d[k] for d in dicts]
            values = normalize_dicts(values)
        else:
            values = np.array([d[k] for d in dicts])
            if values.max() - values.min() != 0:
                values = (values - values.min()) / (values.max() - values.min())
        for d,v in zip(dicts, values):
            d[k] = v
    return dicts


d1 = {'a':1, 'b':1, 'c':{'d':4, 'i':{'j':4}}, 'f':4, 'h':0}
d2 = {'a':3, 'b':3, 'c':{'e':4}, 'g':{}}
d3 = {'a':5, 'c':{'e':2}}
dd = [d1,d2,d3]

pprint(mean_dict(dd))
print()
pprint(normalize_dicts(dd))
