#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---- Third-party libraries ---------------------------------------------------
from conllu import parse
from conllu import parse_tree
import numpy as np
import collections.abc
from collections import OrderedDict as od
from pprint import pprint
from scipy import stats

# ---- Project libraries -------------------------------------------------------
from conll import load_conll, parse_conll, parse_tree_conll


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

def dict_merge(dct, merge_dct):
    # Original: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if k in dct:
            if isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.abc.Mapping):
                dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] += merge_dct[k] # assumes the values are numerical
        else:
            dct[k] = merge_dct[k]

def merge_dicts(dicts):
    """Merges a list of dictionaries"""
    merged = {}
    for d in dicts:
        dict_merge(merged, d)
    return merged


def corpus_stats(trees):
    merged = merge_dicts(tree_stats(tree) for tree in trees)
    
    # Distributions
    rels_branch_patns = sum([len(rel['branches']) for rel in merged['rels'].values()])
    pos_branch_patns = sum([len(pos['branches']) for pos in merged['postags'].values()])
    items_rdist = [v / merged['weight'] for v in merge_dicts(rel['branches'] for rel in merged['rels'].values()).values()]
    pos_pairs_sum = len(merge_dicts(dic['pos_pairs'] for dic in merged['rels'].values())) # total unique pos_pairs
    pos_pairs_set = merge_dicts(dic['pos_pairs'] for dic in merged['rels'].values())
    pos_pairs_corpus_rdist = [p / pos_pairs_sum for p in pos_pairs_set.values()]
    
    # Create a new dictionary
    corpus = {}
    corpus['rels'] = {rel: dict() for rel in merged['rels']}    
    corpus['postags'] = {pos: dict() for pos in merged['postags']}
    
    # Corpus stats
    corpus['mdd'] = merged['mdd'] / len(trees) # MDD
    corpus['mhd'] = merged['mhd'] / len(trees) # MHD
    corpus['depth'] = merged['depth'] / len(trees) # mean depth
    corpus['weight'] = merged['weight'] / len(trees) # mean weight 

    for pos,dic in merged['postags'].items():
        # Pos counts
        corpus['postags'][pos]['r_freq'] = dic['count'] / merged['weight']
        #corpus['postags'][pos]['avg_freq'] = (dic['count'] / len(trees)) / corpus['weight'] = r_freq
        
        # Branch counts
        corpus['postags'][pos]['branches'] = dict()
        corpus['postags'][pos]['branches']['r_branch_patns'] = len(dic['branches']) / pos_branch_patns 
        corpus['postags'][pos]['branches']['left'] = dic['left'] / (dic['left'] + dic['right']) if dic['left'] > 0 else 0 
        corpus['postags'][pos]['branches']['right'] = dic['right'] / (dic['left'] + dic['right']) if dic['right'] > 0 else 0        

        # Branch patterns distribution
        branches_sum = sum([v for v in dic['branches'].values()])
        branches_dist = [v for v in od(sorted(dic['branches'].items())).values()]
        branches_rdist = [v / branches_sum for v in od(sorted(dic['branches'].items())).values()]
        
        corpus['postags'][pos]['branches']['std'] = np.std(branches_rdist) # spread
        corpus['postags'][pos]['branches']['var'] = np.var(branches_rdist) # spread
        corpus['postags'][pos]['branches']['skew'] = stats.skew(branches_dist) # shape
        corpus['postags'][pos]['branches']['mean'] = np.mean(branches_rdist) # location
        corpus['postags'][pos]['branches']['range'] = stats.iqr(branches_rdist) # spread
        corpus['postags'][pos]['branches']['median'] = np.median(branches_rdist) # location
        corpus['postags'][pos]['branches']['kurtosis'] = stats.kurtosis(branches_dist) # shape
        corpus['postags'][pos]['branches']['entropy'] = stats.entropy(branches_rdist) # spread
        corpus['postags'][pos]['branches']['anova'] = stats.f_oneway(items_rdist, branches_rdist)[0] # correlation

    for rel,dic in merged['rels'].items():
        # Rel counts
        corpus['rels'][rel]['r_freq'] = dic['count'] / merged['weight']
        #corpus['rels'][rel]['avg_freq'] = dic['count'] / len(trees)
        
        # Branch counts
        corpus['rels'][rel]['branches'] = dict()
        corpus['rels'][rel]['branches']['r_branch_patns'] = len(dic['branches']) / rels_branch_patns
        corpus['rels'][rel]['branches']['left'] = dic['left'] / (dic['left'] + dic['right']) if dic['left'] > 0 else 0 
        corpus['rels'][rel]['branches']['right'] = dic['right'] / (dic['left'] + dic['right']) if dic['right'] > 0 else 0
       
        # Branch patterns distribution
        branches_sum = sum([v for v in dic['branches'].values()])
        branches_dist = [v for v in od(sorted(dic['branches'].items())).values()]
        branches_rdist = [v / branches_sum for v in od(sorted(dic['branches'].items())).values()]
        
        corpus['rels'][rel]['branches']['std'] = np.std(branches_rdist) # spread
        corpus['rels'][rel]['branches']['var'] = np.var(branches_rdist) # spread
        corpus['rels'][rel]['branches']['skew'] = stats.skew(branches_dist) # shape
        corpus['rels'][rel]['branches']['mean'] = np.mean(branches_rdist) # location
        corpus['rels'][rel]['branches']['range'] = stats.iqr(branches_rdist) # spread
        corpus['rels'][rel]['branches']['median'] = np.median(branches_rdist) # location
        corpus['rels'][rel]['branches']['kurtosis'] = stats.kurtosis(branches_dist) # shape
        corpus['rels'][rel]['branches']['entropy'] = stats.entropy(branches_rdist) # spread
        corpus['rels'][rel]['branches']['anova'] = stats.f_oneway(items_rdist, branches_rdist)[0] # correlation
        
        # Pos-pairs counts
        pos_pairs = sum([v for v in dic['pos_pairs'].values()])
        pos_pairs_dist = sorted([v for v in dic['pos_pairs'].values()], reverse=True)
        pos_pairs_rdist = sorted([v / pos_pairs for v in dic['pos_pairs'].values()], reverse=True)
        
        corpus['rels'][rel]['pos_pairs'] = dict()
        corpus['rels'][rel]['pos_pairs']['r_pos_pairs_patns'] = pos_pairs / pos_pairs_sum
        
        # Pos-pairs distribution
        corpus['rels'][rel]['pos_pairs']['std'] = np.std(pos_pairs_rdist) # spread
        corpus['rels'][rel]['pos_pairs']['var'] = np.var(pos_pairs_rdist) # spread
        corpus['rels'][rel]['pos_pairs']['skew'] = stats.skew(pos_pairs_dist) # shape
        corpus['rels'][rel]['pos_pairs']['mean'] = np.mean(pos_pairs_rdist) # location
        corpus['rels'][rel]['pos_pairs']['range'] = stats.iqr(pos_pairs_rdist) # spread
        corpus['rels'][rel]['pos_pairs']['median'] = np.median(pos_pairs_rdist) # location
        corpus['rels'][rel]['pos_pairs']['kurtosis'] = stats.kurtosis(pos_pairs_dist) # shape
        corpus['rels'][rel]['pos_pairs']['entropy'] = stats.entropy(pos_pairs_rdist) # spread
        corpus['rels'][rel]['pos_pairs']['anova'] = stats.f_oneway(pos_pairs_corpus_rdist, pos_pairs_rdist)[0] # correlation

    return corpus


if __name__ == "__main__":
    path = "data/fr_ftb-ud-dev.conllu"
    trees = parse_tree_conll(path)
#     stats = [tree_stats(tree) for tree in trees]
#     pprint(stats[0])
    pprint(corpus_stats(trees[:100]))
