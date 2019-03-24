#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---- Third-party libraries ---------------------------------------------------
from conllu import parse
from conllu import parse_tree
import numpy as np
import collections

# ---- Project libraries -------------------------------------------------------
from conll import load_conll, parse_conll, parse_tree_conll


def children_per_branch(forest):
    dictionary = dict()  # defines the dictionary var
    for root in forest:
        climb_tree(root, dictionary)
    return dictionary


def climb_tree(root, dictionary):
    count_children(root, dictionary)
    if root.children:
        for child in root.children:
            climb_tree(child, dictionary)

            
def count_children(root, dictionary):
    dictionary.setdefault(root.token['deprel'], dict())
    dictionary[root.token['deprel']].setdefault(str(len(root.children)), 0)
    dictionary[root.token['deprel']][str(len(root.children))] += 1

    
def tree_stats(tree):
    children_stats = [tree_stats(child) for child in tree.children]
    stats = {}
    stats['weight'] = sum([d['weight'] for d in children_stats]) + 1
    stats['depth'] = max([d['depth'] for d in children_stats], default=-1) + 1
    return stats


# def weight(tree):
#     n = 0
#     for child in tree.children:
#         n += weight(child)
#     return n + 1


def weight(tree):
    return 1 + sum([weight(child) for child in tree.children])


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
            if isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping):
                dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] += merge_dct[k] # assumes the values are numerical
        else:
            dct[k] = merge_dct[k]


def rel_stats(tree):
    if tree.children:
        rels = {}
        rels.setdefault(tree.token['deprel'], dict())
        rels[tree.token['deprel']].setdefault(len(tree.children), 1)
        for child in tree.children:
            dict_merge(rels, rel_stats(child))
        return rels
    else:
        return {tree.token['deprel']:{0 : 1}}
    return rels


if __name__ == "__main__":
    path = "data/fr_ftb-ud-dev.conllu"
#     stats = [tree_stats(tree) for tree in parse_tree_conll(path)]
#     mw = np.array([d['weight'] for d in stats]).mean()
#     md = np.array([d['depth'] for d in stats]).mean()
#     print(mw, md)
#     children = children_per_branch(parse_tree_conll(path))
#     print(children.keys())
#     print(children['root'])
    sents = parse_tree_conll(path)
    print("{'relation': {number of immidiate dependents : number of occurences}}")
    print(rel_stats(sents[1]))
