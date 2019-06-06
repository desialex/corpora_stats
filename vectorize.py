#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---- Third-party libraries ---------------------------------------------------
import numpy as np
from pprint import pprint
from scipy import stats
import os
import argparse
import pickle
from collections import OrderedDict as od
import itertools

# ---- Project libraries -------------------------------------------------------
import dictutils as du


def normalize(corpora):
    """
    Normalize the relations and postags across corpora.
    Returns a list of dicts that contain all the relations and postags.
    Parameters:
        corpora: list of dict, each describing one corpus
    Returns:
        None, but dictionaries are modified in situ!
    """
    zero_dict = {'freq': 0, 'branches': {'left': 0, 'right': 0, 'dist': {'kurtosis': 0, 'mean': 0, 'median': 0, 'range': 0, 'skew': 0, 'std': 0}}}
    for key in ['postags', 'rels']: # order is important!
        labels = du.keyset([corpus[key] for corpus in corpora]) # set of relations or postags
        for corpus in corpora:
            for label in labels:
                if label not in corpus[key].keys():
                    corpus[key][label] = dict(zero_dict) # make sure it's a fresh copy!
            # Sanity check
            try:
                min([k in labels for k in corpus[key].keys()]) == True
            except:
                raise Exception("ERROR: alien " + key)
            try:
                assert sorted(corpus[key].keys()) == labels
            except:
                raise Exception("ERROR: couldn't normalize " + key)
        # On second pass, dealing with rels
        zero_dict['pospairs'] = dict()  # adding empty pospairs dict to zero_dict for rels

    # POS pairs
    # When exiting the loop, labels=relations
    pospairs = du.keyset([d['pospairs'] for corpus in corpora for d in corpus['rels'].values()])
    for corpus in corpora:
        for rel, dic in corpus['rels'].items():
            for pair in pospairs:
                if pair not in dic['pospairs'].keys():
                    dic['pospairs'][pair] = 0
            # Sanity check
            try:
                assert rel in labels
            except:
                raise Exception("ERROR: parasitic rel " + rel)
    # Sanity check
    k = [sorted(list(d['pospairs'].keys()) )for corpus in corpora for d in corpus['rels'].values()]
    k.sort()
    try:
        assert len(list(k for k,_ in itertools.groupby(k))) == 1
    except:
        raise Exception("ERROR: couldn't normalize POS pairs")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Vectorize corpora statistics.')
    parser.add_argument('-i', '--inpath', default='data-test/', help='path where the corpora statistics reside')
    parser.add_argument('-o', '--outpath', default='data-test/', help='path where the vectorized data should be saved')
    args = parser.parse_args()
    INPATH = args.inpath
    OUTPATH = args.outpath

    files = sorted([f for f in os.listdir(INPATH) if f.endswith('.pickle')])
    languages = [f[:-7] for f in files]

    # Each pickle is a dict
    corpora = [pickle.load(open(INPATH + file, 'rb')) for file in files]

    # Normalize
    normalize(corpora) # dictionaries are modified in situ

    # Sanity check
    try:
        assert len({du.count_values(c) for c in corpora}) == 1
    except:
        for i, c in enumerate(corpora, 1):
            with open(OUTPATH + 'debug-corpus-{}.txt'.format(i), 'w') as f:
                pprint(c, f)
        raise Exception('ERROR: did not normalize properly, numbers of values differ:\n' + str([du.count_values(c) for c in corpora]))

    # Vectorize
    vectors = du.to_vectors(corpora)

    # Sanity check
    try:
        assert len(vectors) == len(languages)
    except:
        raise Exception('ERROR: number of vectors and number of languages are not equal')
    try:
        assert len({len(v) for v in vectors}) == 1
    except:
        raise Exception('ERROR: vectors are not of equal lengths:\n' + str([len(v) for v in vectors]))

    fn = OUTPATH + 'vectors.pickle'
    with open(fn, 'wb') as f:
        pickle.dump(zip(languages, vectors), f)
