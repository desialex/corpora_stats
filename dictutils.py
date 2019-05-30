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
    Normalize the values of a single dictionary (sum=1).
    NOT recursive. Expects non-negative numerical values.
    """
    if not d: # empty dict
        return d
    else:
        for v in d.values():
            assert isinstance(v, (int, float)), 'Numerical value expected'
            assert v >= 0, 'Non negative value expected'
        values = np.array(list(d.values()))
        if values.sum() != 0:
            values = values / values.sum()
        return dict(zip(d.keys(), values))

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
    return [
        {},
        {'a':1, 'b':2},
        {'a':5, 'c':{'e':2}},
        {'a':3, 'b':3, 'c':{'e':4}, 'g':{}},
        {'a':1, 'b':1, 'c':{'d':4, 'i':{'j':4}}, 'f':4, 'h':0}
    ]

def test_keyset():
    assert keyset(dummies())==['a', 'b', 'c', 'f', 'g', 'h']
    assert keyset(dummies(), typed=True)==[('a', int), ('b', int), ('c', dict), ('f', int), ('g', dict), ('h', int)]

def test_normalize_keys():
    keys = keyset(dummies(), typed=True)
    assert normalize_keys(dummies()[0], keys)=={'a': 0, 'b': 0, 'c': {}, 'f': 0, 'g': {}, 'h': 0}
    assert normalize_keys(dummies()[2], keys)=={'a': 5, 'b': 0, 'c': {'e': 2}, 'f': 0, 'g': {}, 'h': 0}
    keys = keyset(dummies()[0:0], typed=True)
    assert normalize_keys(dummies()[0], keys)=={}
    assert normalize_keys(dummies()[2], keys)=={'a': 5, 'c': {'e': 2}}

def test_normalize_values():
    assert normalize_values(dummies()[0]) == {}
    assert normalize_values(dummies()[1]) == {'a': 0.3333333333333333, 'b': 0.6666666666666666}

def test_normalize_dicts():
    assert normalize_dicts(dummies()) == [
        {'a': 0/5, 'b': 0.0, 'c': {'d': 0.0, 'e': 0.0, 'i': {'j': 0.0}}, 'f': 0.0, 'g': {}, 'h': 0.0},
        {'a': 1/5, 'b': 2/3, 'c': {'d': 0.0, 'e': 0.0, 'i': {'j': 0.0}}, 'f': 0.0, 'g': {}, 'h': 0.0},
        {'a': 5/5, 'b': 0.0, 'c': {'d': 0.0, 'e': 0.5, 'i': {'j': 0.0}}, 'f': 0.0, 'g': {}, 'h': 0.0},
        {'a': 3/5, 'b': 1.0, 'c': {'d': 0.0, 'e': 1.0, 'i': {'j': 0.0}}, 'f': 0.0, 'g': {}, 'h': 0.0},
        {'a': 1/5, 'b': 1/3, 'c': {'d': 1.0, 'e': 0.0, 'i': {'j': 1.0}}, 'f': 1.0, 'g': {}, 'h': 0.0}
    ]
    assert normalize_dicts(dummies()[0:1]) == [{}]
    assert normalize_dicts(dummies()[1:3]) == [{'a': 0.0, 'b': 1.0, 'c': {'e': 0.0}}, {'a': 1.0, 'b': 0.0, 'c': {'e': 1.0}}]

def test_mean_dict():
    assert mean_dict(dummies()[0:1]) == {}
    assert mean_dict(dummies()[0:3]) == {'a': 6/3, 'b': 2/3, 'c': {'e': 2/3}}
    assert mean_dict(dummies()) == {'a': 10/5, 'b': 6/5, 'c': {'d': 4/5, 'e': 6/5, 'i': {'j': 4/5}}, 'f': 4/5, 'g': {}, 'h': 0/5}

def test_merge_into():
    d1 = dummies()[0]
    d2 = dummies()[1]
    d3 = dummies()[2]
    d4 = dummies()[3]
    d5 = dummies()[4]
    merge_into(d1, d2)
    assert d1 == d2
    merge_into(d2, d3)
    assert d2 == {'a': 6, 'b': 2, 'c': {'e': 2}}
    merge_into(d5, d4)
    assert d5 == {'a':4, 'b':4, 'c':{'d':4, 'e':4, 'i':{'j':4}}, 'f':4, 'g':{}, 'h':0}

def test_merge_dicts():
    assert merge_dicts([dummies()[0]]*2) == {}
    assert merge_dicts(dummies()) == {'a': 10, 'b': 6, 'c': {'d': 4, 'e': 6, 'i': {'j': 4}}, 'f': 4, 'g': {}, 'h': 0}

def test():
    test_keyset()
    test_normalize_keys()
    test_normalize_values()
    test_normalize_dicts()
    test_mean_dict()
    test_merge_into()
    test_merge_dicts()

if __name__ == "__main__":
    test()
