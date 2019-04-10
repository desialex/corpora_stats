#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---- Third-party libraries ---------------------------------------------------
from conllu import parse
from conllu import parse_tree
import numpy as np
import collections.abc
from pprint import pprint

# ---- Project libraries -------------------------------------------------------
from conll import load_conll, parse_conll, parse_tree_conll


def tree_stats(tree, root_distance=0):
	stats = {}
	stats['rels'] = {tree.token['deprel']  : {'branching' : {len(tree.children) : 1}, 
																						'count' : 1,
																						'left' : 0,
																						'right' : 0}}
	stats['postags'] = {tree.token['upostag'] : {'branching' : {len(tree.children) : 1},
																							 'count' : 1,
																							 'left' : 0,
																							 'right' : 0}}
	children_stats = [tree_stats(child, root_distance+1) for child in tree.children]
	stats['weight'] = sum([d['weight'] for d in children_stats]) + 1
	stats['depth'] = max([d['depth'] for d in children_stats], default=-1) + 1
	# Dependency distance and hierarchical distance
	if tree.token['head'] == 0: # Tree is the sentence's root
		stats['dd'] = 0
	else:
		stats['dd'] = abs(tree.token['head'] - tree.token['id']) - 1
	stats['hd'] = root_distance
	stats['ddsum'] = sum([d['ddsum'] for d in children_stats]) + stats['dd']
	stats['hdsum'] = sum([d['hdsum'] for d in children_stats]) + stats['hd']
	stats['rels'] = merge_dicts([stats['rels']] + [d['rels'] for d in children_stats])
	stats['postags'] = merge_dicts([stats['postags']] + [d['postags'] for d in children_stats])
	if stats['weight'] > 1:
		stats['mdd'] = stats['ddsum'] / (stats['weight'] - 1)
		stats['mhd'] = stats['hdsum'] / (stats['weight'] - 1)	
	else:
		stats['mdd'] = 0
		stats['mhd'] = 0
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

# def rel_stats(tree):
# 	if tree.children:
# 		rels = {}
# 		rels.update({tree.token['deprel']  : {'branching' : {len(tree.children) : 1}, 
# 																					'count' : 1,
# 																					'lr_branching' : {'left' : 0, 'right' : 0}}})
# 		rels.update({tree.token['upostag'] : {'branching' : {len(tree.children) : 1},
# 																					'count' : 1,
# 																					'lr_branching' : {'left' : 0, 'right' : 0}}})
# 		for child in tree.children: 
# 			dict_merge(rels, rel_stats(child))
# 			rels[child.token['deprel']].setdefault('gPOS:dPOS', dict())
# 			rels[child.token['deprel']]['gPOS:dPOS'].setdefault(str(tree.token['upostag'])+':'+
# 																str(child.token['upostag']), 1)
# 			if child.token['id'] < tree.token['id']:
# 				rels[tree.token['deprel']]['lr_branching']['left'] += 1
# 				rels[tree.token['upostag']]['lr_branching']['left'] += 1
# 			else:
# 				rels[tree.token['deprel']]['lr_branching']['right'] += 1
# 				rels[tree.token['upostag']]['lr_branching']['right'] += 1
# 		return rels
# 	else:
# 		return {tree.token['deprel']:{'branching' : {0 : 1}, 'count' : 1}, 
# 			   tree.token['upostag']:{'branching' : {0 : 1}, 'count' : 1}}


if __name__ == "__main__":
	path = "data/test.conllu"
	trees = parse_tree_conll(path)
	stats = [tree_stats(tree) for tree in trees]
	pprint(stats[0])
