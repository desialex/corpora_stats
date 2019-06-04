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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Vectroize corpora statistics.')
    parser.add_argument('-i', '--inpath',
                        default='data-test/',
                        help='path where the corpora statistics reside')
    parser.add_argument('-o', '--outpath',
                        default='data-test/',
                        help='path where the vectorized data should be saved')
    args = parser.parse_args()
    INPATH = args.inpath
    OUTPATH = args.outpath

    files = sorted([f for f in os.listdir(INPATH) if f.endswith('.pickle')])
    languages = [f[:-7] for f in files]

    # Each pickle is a dictionary
    corpora = [pickle.load(open(INPATH + file, 'rb')) for file in files]

    keys = du.keyset(corpora)

    print(keys)

    for corpus in corpora:
        pprint(corpus)
