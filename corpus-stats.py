#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Third-party libraries
from conllu import parse, parse_tree
import numpy as np
from pprint import pprint
from scipy import stats
import os
import pickle
from collections import OrderedDict as od
# Project libraries
from conll import load_conll, parse_conll, parse_tree_conll
import dictutils as du

# PARAMETERS
# ==============================================================================
# Must include final '/'
UD_PATH = '/Users/francois/Dropbox/job/data/UD_2.4/merged/'
DATA_PATH = 'data/'
# ==============================================================================

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
    stats['rels'] = du.merge_dicts([stats['rels']] + [c['rels'] for c in children_stats])
    stats['postags'][pos]['right'] = right
    stats['postags'][pos]['left'] = left
    stats['postags'] = du.merge_dicts([stats['postags']] + [c['postags'] for c in children_stats])

    # Gov and dep POS for relations
    stats['rels'][rel]['pos_pairs'] = {(gov_pos, pos): 1}

    return stats

def describe_dist(dist, rdist, ref_rdist):
    d = {}
    d['mean'] = np.mean(rdist) # location
    d['median'] = np.median(rdist) # location
    d['std'] = np.std(rdist) # spread
    d['var'] = np.var(rdist) # spread
    d['range'] = stats.iqr(rdist) # spread
    d['entropy'] = stats.entropy(rdist) # spread
    d['skew'] = stats.skew(dist) # shape
    d['kurtosis'] = stats.kurtosis(dist) # shape
    d['anova'] = stats.f_oneway(ref_rdist, rdist)[0] # correlation
    return d

def corpus_stats(trees):
    
    size = len(trees)
    merged = du.merge_dicts([tree_stats(tree) for tree in trees]) # values are added

    # Distributions
    items_rdist = [v / merged['weight'] for v in du.merge_dicts(rel['branches'] for rel in merged['rels'].values()).values()]
    pos_pairs_sum = len(du.merge_dicts(dic['pos_pairs'] for dic in merged['rels'].values())) # total unique pos_pairs

    # Create a new dictionary
    corpus = {}
    corpus['rels'] = {rel: dict() for rel in merged['rels']}
    corpus['postags'] = {pos: dict() for pos in merged['postags']}
    # corpus['pos_rel_pos'] = du.normalize_values({(key[0], rel, key[1]): value for rel,dic in merged['rels'].items() for key,value in dic['pos_pairs'].items()})

    # Corpus stats (means)
    corpus['mdd'] = merged['mdd'] / size # MDD
    corpus['mhd'] = merged['mhd'] / size # MHD
    corpus['depth'] = merged['depth'] / size # mean depth
    corpus['weight'] = merged['weight'] / size # mean weight

    for key in ['rels', 'postags']:

        # Distribution
        branch_patns = sum([len(pos_rel['branches']) for pos_rel in merged[key].values()])

        for pos_rel, dic in merged[key].items():

            # Counts
            corpus[key][pos_rel]['r_freq'] = dic['count'] / merged['weight']

            # Branch pattern distribution
            branches_sum = sum([v for v in dic['branches'].values()])
            branches_dist = [v for v in od(sorted(dic['branches'].items())).values()]
            branches_rdist = [v / branches_sum for v in od(sorted(dic['branches'].items())).values()]
            corpus[key][pos_rel]['branches'] = describe_dist(branches_dist, branches_rdist, items_rdist)

            # Branch counts
            corpus[key][pos_rel]['branches']['r_branch_patns'] = len(dic['branches']) / branch_patns
            corpus[key][pos_rel]['branches']['left'] = dic['left'] / (dic['left'] + dic['right']) if dic['left'] > 0 else 0
            corpus[key][pos_rel]['branches']['right'] = dic['right'] / (dic['left'] + dic['right']) if dic['right'] > 0 else 0

            # # Pos-pairs
            # if key=='postags':
            #     pos_pairs = sum([v for v in dic['pos_pairs'].values()])
            #     corpus[key][pos_rel]['r_pos_pairs_patns'] = pos_pairs / pos_pairs_sum

    return corpus

def sanity_check(data):
    # assert round(sum(data['pos_rel_pos'].values()), 15) == 1
    for key in ['postags', 'rels']:
        assert round(sum([d['r_freq'] for d in data[key].values()]), 15) == 1
        branches = [d['branches'] for d in data[key].values()]
        assert min([round(b['left'] + b['right'], 15) in {0,1} for b in branches]) == True
        # We have a 0 sum when there are no dependents
    # vector = du.to_vector(st)
    # pprint(vector)
    # pprint(st)

if __name__ == "__main__":

    files = sorted([f for f in os.listdir(UD_PATH) if f.endswith('.conllu')])
    languages = [f[:-7] for f in files]

    for file, lng in zip(files, languages):
        print('Processing', lng)

        try:
            corpus = parse_tree_conll(UD_PATH + file)
        except:
            print("  SKIPPING: can't parse", file)
            continue

        try:
            data = corpus_stats(corpus)
        except:
            print("  SKIPPING: can't process the corpus for", lng)
            continue

        try:
            sanity_check(data)
        except:
            print("  SKIPPING: flushing inconsistent data for", lng)
            continue

        fn = DATA_PATH + lng + '.pickle'
        with open(fn, 'wb') as f:
            pickle.dump(data, f)
