#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pickle
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from pprint import pprint

if __name__ == "__main__":
    file = 'stats.pickle'
    with open(file, 'rb') as f:
        data = pickle.load(f)
    # Leave out the ones with wrong vector length
    data = {k:v for k,v in data.items() if len(v) == 12779}
    X = np.vstack(data.values())
    languages = list(data.keys())

    # 2D projection
    pca = PCA(n_components=2, whiten=True)
    pca.fit(X)
    X_2d = pca.transform(X)
    fig = plt.figure(figsize=(20, 20))
    for ((x,y), language) in zip(X_2d, languages):
        plt.scatter(x, y)
        plt.annotate(language, (x,y))
    plt.savefig('scatter.png')

    # Dendrogram
    Z = linkage(X, 'single')
    fig = plt.figure(figsize=(12, 10))
    dn = dendrogram(Z, labels=languages)
    fig.savefig('dendrogram.png')

    # K-means
    with open('data/categories.txt') as f:
        families = [l.strip() for l in f.readlines()]
    k = len(families)
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(X)
    y_kmeans = kmeans.predict(X)
    clusters = {}
    for language, fam_id in zip(languages, y_kmeans):
        if fam_id in clusters.keys():
            clusters[fam_id].append(language)
        else:
            clusters[fam_id] = [language]
    with open('kmeans.txt', 'w') as f:
        pprint(clusters, stream=f)
