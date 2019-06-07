import pickle
import numpy as np
from sklearn import metrics
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import precision_recall_fscore_support, classification_report

# UD 2.4 dataset
gold = [6, 0, 0, 6, 0, 6, 0, 9, 4, 6, 6, 6, 10, 12, 6, 12, 12, 0, 6, 6, 6, 6, 6, 16, 16, 6, 16, 6, 6, 6, 6, 6, 0, 6, 16, 3, 6, 6, 7, 16, 15, 16, 8, 6, 6, 6, 6, 0, 6, 14, 6, 16, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 3, 5, 5, 13, 15, 6, 6, 6, 15, 2, 11, 6, 1, 1]
families = ['Afro-Asiatic', 'Atlantic-Congo', 'Austroasiatic', 'Austronesian', 'Basque', 'Dravidian', 'IE', 'Japonic', 'Koreanic', 'Mande', 'Mongolic', 'Pama-Nyungan', 'Sino-Tibetan', 'Tai-Kadai', 'Tupian', 'Turkic', 'Uralic']

data = open('data-test/vectors-all.pickle', 'rb')
vectors = list(pickle.load(data))
labels = [t[0] for t in vectors]
matrix = np.asarray([t[1] for t in vectors], dtype=np.float32)
len(matrix[0])

# Clustering scikit-learn
cluster = AgglomerativeClustering(n_clusters=17, affinity='euclidean', linkage='average')
predicted = cluster.fit_predict(matrix)
metrics.fowlkes_mallows_score(gold, predicted)

# Clustering and Dendrogram scipy
Z = linkage(matrix, method='ward')
fig = plt.figure(figsize=(12, 10), dpi=300)
dn = dendrogram(Z, labels=labels)
fig.savefig('dend.png')
plt.close('all')


# Chen and Gerdes dataset
languages = ['Ancient_Greek', 'Arabic', 'Basque', 'Bulgarian', 'Catalan', 'Chinese', 'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Estonian', 'Finnish', 'French', 'Galician', 'German', 'Gothic', 'Greek', 'Hebrew', 'Hindi', 'Hungarian', 'Indonesian', 'Irish', 'Italian', 'Japanese', 'Korean', 'Latin', 'Latvian', 'Norwegian', 'Old_Church_Slavonic', 'Persian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Slovak', 'Slovenian', 'Spanish', 'Swedish', 'Turkish', 'Ukrainian', 'Urdu', 'Vietnamese']
families = ['Afro-Asiatic', 'Austroasiatic', 'Austronesian', 'Basque', 'IE', 'Japanese', 'Korean', 'Sino-Tibetan', 'Turkic', 'Uralic']
gold_sub = [4, 0, 3, 4, 4, 7, 4, 4, 4, 4, 4, 9, 9, 4, 4, 4, 4, 4, 0, 4, 9, 2, 4, 4, 5, 6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8, 4, 4, 1]
pred = [1, 0, 1, 1, 1, 7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 2, 1, 5, 6, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 8, 1, 9, 1]
metrics.fowlkes_mallows_score(gold_sub, pred)
precision_recall_fscore_support(gold_sub, pred, average='weighted')
print(classification_report(gold_sub, pred, target_names=families))
# UD 2.4 subset identical to Chen and Gerdes
matrix = np.asarray([t[1] for t in vectors if t[0] in gerdes_dataset], dtype=np.float32)
cluster = AgglomerativeClustering(n_clusters=10, affinity='euclidean', linkage='average')
predicted = cluster.fit_predict(matrix)
metrics.fowlkes_mallows_score(gold_sub, predicted)
precision_recall_fscore_support(gold_sub, predicted, average='weighted')
print(classification_report(gold_sub, predicted, target_names=labels))
