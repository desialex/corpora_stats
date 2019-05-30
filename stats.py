#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---- Third-party libraries ---------------------------------------------------
from conllu import parse
from conllu import parse_tree
import numpy as np
from pprint import pprint
from scipy import stats
import os
import pickle
from collections import OrderedDict as od

# ---- Project libraries -------------------------------------------------------
from conll import load_conll, parse_conll, parse_tree_conll
import dictutils as du


def tree_stats(tree, root_distance=0, gov_pos='ROOT'):

    # Initialize dictionary
    stats = {}
    stats['root_id'] = tree.token['id']
    rel = tree.token['deprel']
    pos = tree.token['upostag']
    stats['rels'] = {rel: {'branches': {len(tree.children): 1},
                           'count': 1}}
    stats['postags'] = {pos: {'branches': {len(tree.children): 1},
                              'count': 1}}

    # Get stats for all children (children_stats is a list of stat dictionaries)
    children_stats = [tree_stats(child, root_distance+1, tree.token['upostag']) for child in tree.children]

    # Weight and depth
    stats['weight'] = sum([c['weight'] for c in children_stats]) + 1
    stats['depth'] = max([c['depth'] for c in children_stats], default=-1) + 1

    # Dependency distance and hierarchical distance
    if tree.token['head'] == 0: # Tree is the sentence's root
        stats['dd'] = 0
    else:
        stats['dd'] = abs(tree.token['head'] - tree.token['id']) - 1
    stats['hd'] = root_distance
    stats['ddsum'] = sum([c['ddsum'] for c in children_stats]) + stats['dd']
    stats['hdsum'] = sum([c['hdsum'] for c in children_stats]) + stats['hd']

    # Mean dependency distance and mean hierarchical distance
    if stats['weight'] > 1:
        stats['mdd'] = stats['ddsum'] / (stats['weight'] - 1)
        stats['mhd'] = stats['hdsum'] / (stats['weight'] - 1)
    else:
        stats['mdd'] = 0
        stats['mhd'] = 0

    # Branching and count stats for relations and POS tags
    right = sum([True for c in children_stats if c['root_id']-stats['root_id'] > 0])
    left = sum([True for c in children_stats if c['root_id']-stats['root_id'] < 0])
    stats['rels'][rel]['right'] = right
    stats['rels'][rel]['left'] = left
    stats['rels'] = merge_dicts([stats['rels']] + [c['rels'] for c in children_stats])
    stats['postags'][pos]['right'] = right
    stats['postags'][pos]['left'] = left
    stats['postags'] = merge_dicts([stats['postags']] + [c['postags'] for c in children_stats])

    # Gov and dep POS for relations
    stats['rels'][rel]['pos_pairs'] = {(gov_pos, pos): 1}

    return stats

def describe_dist(dist, rdist, ref_rdist):
    d = {}
    d['std'] = np.std(rdist) # spread
    d['var'] = np.var(rdist) # spread
    d['skew'] = stats.skew(dist) # shape
    d['mean'] = np.mean(rdist) # location
    d['range'] = stats.iqr(rdist) # spread
    d['median'] = np.median(rdist) # location
    d['kurtosis'] = stats.kurtosis(dist) # shape
    d['entropy'] = stats.entropy(rdist) # spread
    d['anova'] = stats.f_oneway(ref_rdist, rdist)[0] # correlation
    return d

def corpus_stats(trees):
    merged = merge_dicts(tree_stats(tree) for tree in trees)

    # Distributions
    rels_branch_patns = sum([len(rel['branches']) for rel in merged['rels'].values()])
    pos_branch_patns = sum([len(pos['branches']) for pos in merged['postags'].values()])
    items_rdist = [v / merged['weight'] for v in merge_dicts(rel['branches'] for rel in merged['rels'].values()).values()]
    pos_pairs_sum = len(merge_dicts(dic['pos_pairs'] for dic in merged['rels'].values())) # total unique pos_pairs

    # Create a new dictionary
    corpus = {}
    corpus['rels'] = {rel: dict() for rel in merged['rels']}
    corpus['postags'] = {pos: dict() for pos in merged['postags']}
    corpus['pos_rel_pos'] = {(key[0], rel, key[1]): value for rel,dic in merged['rels'].items() for key,value in dic['pos_pairs'].items()}

    # Corpus stats
    corpus['mdd'] = merged['mdd'] / len(trees) # MDD
    corpus['mhd'] = merged['mhd'] / len(trees) # MHD
    corpus['depth'] = merged['depth'] / len(trees) # mean depth
    corpus['weight'] = merged['weight'] / len(trees) # mean weight

    for pos,dic in merged['postags'].items():

        # Pos counts
        corpus['postags'][pos]['r_freq'] = dic['count'] / merged['weight']

        # Branch patterns distribution
        branches_sum = sum([v for v in dic['branches'].values()])
        branches_dist = [v for v in od(sorted(dic['branches'].items())).values()]
        branches_rdist = [v / branches_sum for v in od(sorted(dic['branches'].items())).values()]
        corpus['postags'][pos]['branches'] = describe_dist(branches_dist, branches_rdist, items_rdist)

        # Branch counts
        corpus['postags'][pos]['branches']['r_branch_patns'] = len(dic['branches']) / pos_branch_patns
        corpus['postags'][pos]['branches']['left'] = dic['left'] / (dic['left'] + dic['right']) if dic['left'] > 0 else 0
        corpus['postags'][pos]['branches']['right'] = dic['right'] / (dic['left'] + dic['right']) if dic['right'] > 0 else 0

    for rel,dic in merged['rels'].items():

        # Rel counts
        corpus['rels'][rel]['r_freq'] = dic['count'] / merged['weight']

        # Branch patterns distribution
        branches_sum = sum([v for v in dic['branches'].values()])
        branches_dist = [v for v in od(sorted(dic['branches'].items())).values()]
        branches_rdist = [v / branches_sum for v in od(sorted(dic['branches'].items())).values()]
        corpus['rels'][rel]['branches'] = describe_dist(branches_dist, branches_rdist, items_rdist)

        # Branch counts
        corpus['rels'][rel]['branches']['r_branch_patns'] = len(dic['branches']) / rels_branch_patns
        corpus['rels'][rel]['branches']['left'] = dic['left'] / (dic['left'] + dic['right']) if dic['left'] > 0 else 0
        corpus['rels'][rel]['branches']['right'] = dic['right'] / (dic['left'] + dic['right']) if dic['right'] > 0 else 0

        # Pos-pairs
        pos_pairs = sum([v for v in dic['pos_pairs'].values()])
        corpus['rels'][rel]['r_pos_pairs_patns'] = pos_pairs / pos_pairs_sum

    return corpus

def vectorize_dicts(dicts):
    """Returns a list of normalized vectors for a list of dictionaries"""
    keys = keyset(dicts)
    vectors = []
    for d in dicts:
        d = normalize_values(d)
        vector = []
        for k in keys:
            if k in d.keys():
                vector.append(d[k])
            else:
                vector.append(0)
        vectors.append(vector)
    return vectors

def flatten(dictionary):
    """Flattens a dictionary (and embedded dictionaries) to a vector"""
    ordered = od(dictionary)
    vector = np.array([])
    for k, v in ordered.items():
        if isinstance(v, dict):
            # np.append doesn't work like list.append
            # if the element to append is a list, it is
            # concatenated element-wise
            vector = np.append(vector, flatten(v))
        else:
            vector = np.append(vector, v)
    return vector

def vectorize(dic, keyset, section):
    """Creates a normalized vector per keyset"""
    vector = np.array([])
    key_len = 0
    for key in keyset:
        # To be rewritten!
        if section == 'postags':
            if key in dic[section]:
                vector = np.append(vector, flatten(dic[section][key]))
            else:
                vector = np.append(vector, [0]*13) # hardcoded value
        else: # section == 'rels'
            if key in dic[section]:
                vector = np.append(vector, flatten(dic[section][key]))
            else:
                vector = np.append(vector, [0]*14) # hardcoded value
    return vector

def get_vectors(dicts):
    """Transforms dicts to equal length vectors"""
    pos_keyset = keyset([c['postags'] for c in dicts])
    rel_keyset = keyset([c['rels'] for c in dicts])

    v0 = [list(v for (k,v) in dic.items() if not isinstance(dic[k], dict)) for dic in dicts] # maybe also od(dict)?
    v1 = [vectorize(dic, pos_keyset, 'postags') for dic in dicts]
    v2 = [vectorize(dic, rel_keyset, 'rels') for dic in dicts]
    v3 = np.array(vectorize_dicts([dic['pos_rel_pos'] for dic in dicts]))
    vectors = [np.concatenate([a for a in v]) for v in list(zip(v0, v1, v2, v3))]

    return vectors

def test():
    trees = parse_tree_conll('data/test1.conllu')
    st = corpus_stats(trees)
    print(len(trees), 'trees')
    pprint(st)

if __name__ == "__main__":
    test()
    # dir = 'data'
    # languages = [f[:-7] for f in os.listdir(dir) if f.endswith('.conllu')]
    # files = [dir+'/'+lng+'.conllu' for lng in languages]
    # corpora = [corpus_stats(parse_tree_conll(file)) for file in files]
    # vectors = get_vectors(corpora)
    # np.save('vectors', vectors)
    # data = dict(zip(languages, vectors))
    # with open('stats.pickle', 'wb') as f:
    #     pickle.dump(data, f)
