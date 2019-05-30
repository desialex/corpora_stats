import numpy as np
from pprint import pprint
import collections.abc

def keyset(dicts, typed=False):
    """
    Takes a list of dictionaries and returns the list of all keys (and value
    types if typed=True)
    """
    if typed:
        return sorted(set([(k,type(d[k])) for d in dicts for k in d.keys()]))
    else:
        return sorted(set([k for d in dicts for k in d.keys()]))

def normalize_keys(d, keys):
    """
    Normalize the keys in a dictionary. NOT recursive.
    Parameters:
        d (dict): a dictionary that needs to be normalized
        keys (list): (key, type) tuples, where type is the type of value
                     expected for key
    Returns a dict that contains all the specified keys
    """
    for k,t in keys:
        if k not in d.keys():
            d[k] = t() # creates a new instance of class t with null value
    return d

def normalize_values(d):
    """
    Normalize the values of a single dictionary (offset and scale)
    """
    values = np.array(d.values())
    values = (values - values.min()) / (values.max() - values.min())
    return dict(zip(d.keys(),values))

def normalize_dicts(dicts):
    """
    Normalize keys and values across a list of dictionaries (offset and scale)
    """
    keys = keyset(dicts, typed=True) # list of keys and types
    dicts = [normalize_keys(d, keys) for d in dicts] # make sure we have the same keys
    for k,t in keys: # k: key, t: type
        if str(t) == "<class 'dict'>":
            values = [d[k] for d in dicts]
            values = normalize_dicts(values)
        else:
            values = np.array([d[k] for d in dicts])
            if values.max() - values.min() != 0: # avoid dividing by zero
                values = (values - values.min()) / (values.max() - values.min())
            else:
                values = np.zeros(values.shape)
        for d,v in zip(dicts, values): # d: dict, v: value
            d[k] = v
    return dicts

def mean_dict(dicts):
    """
    Takes a list of dicts and returns a dict with mean values
    Assuming values are int/float or dict
    """
    keys = keyset(dicts, typed=True) # list of keys and types
    dicts = [normalize_keys(d, keys) for d in dicts] # make sure we have the same keys
    mean = {}
    for k,t in keys:
        values = [d[k] for d in dicts]
        if str(t) == "<class 'dict'>":
            mean[k] = mean_dict(values)
        else:
            mean[k] = np.mean(values)
    return mean

def merge_into(dict_into, dict_from):
    # Original: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    """
    Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys.
    Paramenters:
        dict_into (dict): dict into which to merge
        dict_from (dict): dict to merge into dict_into
    Returns: None
    """
    for k, v in dict_from.items():
        if k in dict_into:
            if isinstance(dict_from[k], collections.abc.Mapping) and isinstance(dict_into[k], collections.abc.Mapping):
                merge_into(dict_into[k], dict_from[k])
            else:
                dict_into[k] += dict_from[k] # assumes the values are numerical
        else:
            dict_into[k] = dict_from[k]

def merge_dicts(dicts):
    """Merges a list of dictionaries into one"""
    merged = {}
    for d in dicts:
        merge_into(merged, d)
    return merged


# TEST ROUTINES
# ===================================================================

def dummies():
    """ Dummy dicts to use for testing"""
    d0 = {}
    d1 = {'a':5, 'c':{'e':2}}
    d2 = {'a':3, 'b':3, 'c':{'e':4}, 'g':{}}
    d3 = {'a':1, 'b':1, 'c':{'d':4, 'i':{'j':4}}, 'f':4, 'h':0}
    return [d0, d1, d2, d3]

def test_keyset():
    dicts = dummies()
    assert(keyset(dicts)==['a', 'b', 'c', 'f', 'g', 'h'])
    assert(keyset(dicts, typed=True)==[('a', int), ('b', int), ('c', dict), ('f', int), ('g', dict), ('h', int)])

def test_normalize_keys():
    dicts = dummies()
    keys = keyset(dicts, typed=True)
    assert(normalize_keys(dicts[0], keys)=={'a': 0, 'b': 0, 'c': {}, 'f': 0, 'g': {}, 'h': 0})
    assert(normalize_keys(dicts[1], keys)=={'a': 5, 'b': 0, 'c': {'e': 2}, 'f': 0, 'g': {}, 'h': 0})
    dicts = dummies()
    keys = keyset(dicts[0:0], typed=True)
    assert(normalize_keys(dicts[0], keys)=={})
    assert(normalize_keys(dicts[1], keys)=={'a': 5, 'c': {'e': 2}})

# def test_normalize_values():
# def test_normalize_dicts():
# def test_mean_dict():
# def test_merge_into():
# def test_merge_dicts():

def test():
    test_keyset()
    test_normalize_keys()
