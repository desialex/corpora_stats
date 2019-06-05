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

# ---- Project libraries -------------------------------------------------------
import dictutils as du


def normalize_rels_postags(corpora):
    """
    Normalize the relations and postags across corpora.
    Returns a list of dicts that contain all the relations and postags.
    Parameters:
        corpora: list of dict, each describing one corpus
    Returns:
        None, but dictionaries are modified in situ!
    """
    zero_dict = {'branches': {'dist': {'kurtosis': 0, 'mean': 0, 'median': 0, 'range': 0, 'skew': 0, 'std': 0}, 'left': 0, 'right': 0}, 'freq': 0}
    for key in ['rels', 'postags']:
        labels = du.keyset([corpus[key] for corpus in corpora])
        for corpus in corpora:
            for label in labels:
                if label not in corpus[key].keys():
                    corpus[key][label] = zero_dict


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Vectroize corpora statistics.')
    parser.add_argument('-i', '--inpath', default='data-test/', help='path where the corpora statistics reside')
    parser.add_argument('-o', '--outpath', default='data-test/', help='path where the vectorized data should be saved')
    args = parser.parse_args()
    INPATH = args.inpath
    OUTPATH = args.outpath

    files = sorted([f for f in os.listdir(INPATH) if f.endswith('.pickle')])
    languages = [f[:-7] for f in files]

    # Each pickle is a dict
    corpora = [pickle.load(open(INPATH + file, 'rb')) for file in files]
    normalize_rels_postags(corpora) # dictionaries are modified in situ
    vectors = du.to_vectors(corpora)

    # Sanity check
    try:
        assert len({len(v) for v in vectors}) == 1
    except:
        raise Exception('ERROR: Vectors are not of equal lengths')
    try:
        assert len(vectors) == len(languages)
    except:
        raise Exception('ERROR: Number of vectors and number of languages are not equal')

    fn = OUTPATH + 'vectors.pickle'
    with open(fn, 'wb') as f:
        pickle.dump(zip(languages, vectors), f)
