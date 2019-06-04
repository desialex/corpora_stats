#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Third-party libraries
import numpy as np
from pprint import pprint
import scipy.stats
import os
import pickle

# Project libraries
from conll import parse_tree_conll
import dictutils as du
import argparse


def tree_stats(tree, root_distance=0, gov_pos='ROOT'):

    # Initialize dictionary
    stats = {}
    stats['root_id'] = tree.token['id']
    rel = tree.token['deprel']
    pos = tree.token['upostag']
    stats['rels'] = {rel: {'branches': [len(tree.children)], 'count': 1}}
    stats['postags'] = {pos: {'branches': [len(tree.children)], 'count': 1}}

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

    return stats


def describe_dist(dist):
    # Sanity check
    try:
        assert isinstance(dist, list)
        assert min([True for v in dist if isinstance(v, (int, float))]) == True
    except:
        raise ValueError('cannot decribe as a curve {}'.format(dist))

    d = {}
    d['mean'] = np.mean(dist) # location
    d['median'] = np.median(dist) # location
    d['std'] = np.std(dist) # spread
    # d['var'] = np.var(dist) # spread
    d['range'] = scipy.stats.iqr(dist) # spread
    # d['entropy'] = scipy.stats.entropy(dist) # spread
    d['skew'] = scipy.stats.skew(dist) # shape
    d['kurtosis'] = scipy.stats.kurtosis(dist) # shape
    return d


def corpus_stats(trees):

    size = len(trees)
    merged = du.merge_dicts([tree_stats(tree) for tree in trees]) # values are summed

    # Initialize dictionary
    corpus = {}
    corpus['rels'] = {rel: dict() for rel in merged['rels'].keys()}
    corpus['postags'] = {pos: dict() for pos in merged['postags'].keys()}

    # Corpus stats (means)
    corpus['mdd'] = merged['mdd'] / size # MDD
    corpus['mhd'] = merged['mhd'] / size # MHD
    corpus['depth'] = merged['depth'] / size # mean depth
    corpus['weight'] = merged['weight'] / size # mean weight

    # Processing merged['rels'] and merged['postags'] the same way
    for key in ['rels', 'postags']:
        for pos_rel, dic in merged[key].items():
            # print(key, pos_rel)
            # pos_rel is the key for (a relation or a postag)
            # dic is the value (dict with branching and count information)

            # Relative frequency
            corpus[key][pos_rel]['freq'] = dic['count'] / merged['weight']

            # Sanity check
            try:
                assert dic['left'] + dic['right'] == sum(dic['branches'])
                assert len(dic['branches']) == dic['count' ]
            except:
                raise ValueError('Inconsistent values for {}'.format(pos_rel))

            # Branching
            corpus[key][pos_rel]['branches'] = {}
            sum_branches = sum(dic['branches'])
            corpus[key][pos_rel]['branches']['dist'] = describe_dist(dic['branches'])
            corpus[key][pos_rel]['branches']['left'] = dic['left'] / sum_branches if sum_branches > 0 else 0
            corpus[key][pos_rel]['branches']['right'] = dic['right'] / sum_branches if sum_branches > 0 else 0

    return corpus


def sanity_check(data):
    for key in ['postags', 'rels']:
        assert round(sum([d['freq'] for d in data[key].values()]), 15) == 1
        branches = [d['branches'] for d in data[key].values()]
        assert min([round(b['left'] + b['right'], 15) in {0,1} for b in branches]) == True
        # We have a 0 sum when there are no dependents


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get statistics for each corpus.')
    parser.add_argument('-i', '--inpath', default='data-test/', help='path where the corpora reside')
    parser.add_argument('-o', '--outpath', default='data-test/', help='path where the statistics should be saved')
    args = parser.parse_args()
    UD_PATH = args.inpath
    DATA_PATH = args.outpath

    files = sorted([f for f in os.listdir(UD_PATH) if f.endswith('.conllu')])
    languages = [f[:-7] for f in files]
    pickled = [f for f in os.listdir(DATA_PATH) if f.endswith('.pickle')]
    done = [f[:-7] for f in pickled]

    for file, lng in zip(files, languages):

        if lng in done:
            continue

        print('Processing', lng)

        try:
            corpus = parse_tree_conll(UD_PATH + file)
        except:
            print("  SKIPPING: can't parse", file)
            continue

        try:
            data = corpus_stats(corpus)
        except ValueError as err:
            print('  SKIPPING: '+str(err))
            continue
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
