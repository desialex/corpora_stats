#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pickle
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt
from pprint import pprint

if __name__ == "__main__":
    file = 'stats.pickle'
    with open(file, 'rb') as f:
        data = pickle.load(f)
    # Leave out the ones with wrong vector length
    data = {k:v for k,v in data.items() if len(v) == 12779}
    X = np.vstack(data.values())
    Z = linkage(X)
    fig = plt.figure(figsize=(12, 10))
    dn = dendrogram(Z, labels=list(data.keys()))
    plt.savefig('clusters.png')
