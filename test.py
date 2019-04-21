import numpy as np
import pickle
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from pprint import pprint


vecs = np.load('vectors.npy')
vectors = np.array([v for v in vecs if len(v) == 12779])
norm_vecs = np.array([]).reshape(0,12779)
for vec in vectors:
    nvec = (vec - vec.min()) / (vec.max() - vec.min())
    norm_vecs = np.vstack([norm_vecs, nvec])
np.save('norm_vecs_h', norm_vecs)


file = 'stats.pickle'
with open(file, 'rb') as f:
    data = pickle.load(f)
# Leave out the ones with wrong vector length
data = {k:v for k,v in data.items() if len(v) == 12779}
X = norm_vecs # np.vstack(data.values())
languages = list(data.keys())


# Dendrogram
Z = linkage(X, 'single')
fig = plt.figure(figsize=(12, 10), dpi=300)
dn = dendrogram(Z, labels=languages)
fig.savefig('dendrogram_norm_h.png')