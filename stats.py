#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---- Third-party libraries ---------------------------------------------------
from conllu import parse
from conllu import parse_tree
import numpy as np

# ---- Project libraries -------------------------------------------------------
from conll import load_conll, parse_conll, parse_tree_conll


def children_per_branch(forest):
    dictionary = dict()  # defines the dictionary var
    for root in forest:
        climb_tree(root, dictionary)
    return dictionary


def tree_stats(tree):
    children_stats = [tree_stats(child) for child in tree.children]
    stats = {}
    stats['weight'] = sum([d['weight'] for d in children_stats]) + 1
    stats['depth'] = max([d['depth'] for d in children_stats], default=-1) + 1
    return stats


def climb_tree(root, dictionary):
    count_children(root, dictionary)
    if root.children:
        for child in root.children:
            climb_tree(child, dictionary)

def count_children(root, dictionary):
    dictionary.setdefault(root.token['deprel'], dict())
    dictionary[root.token['deprel']].setdefault(str(len(root.children)), 0)
    dictionary[root.token['deprel']][str(len(root.children))] += 1


# def weight(tree):
#     n = 0
#     for child in tree.children:
#         n += weight(child)
#     return n + 1


def weight(tree):
    return 1 + sum([weight(child) for child in tree.children])
        
if __name__ == "__main__":
    path = "data/fr_ftb-ud-dev.conllu"
    stats = [tree_stats(tree) for tree in parse_tree_conll(path)]
    mw = np.array([d['weight'] for d in stats]).mean()
    md = np.array([d['depth'] for d in stats]).mean()
    print(mw, md)
#     children = children_per_branch(parse_tree_conll(path))
#     print(children.keys())
#     print(children['root'])
