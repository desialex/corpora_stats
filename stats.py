#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---- Third-party libraries ---------------------------------------------------
from conllu import parse
from conllu import parse_tree

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
        
        
if __name__ == "__main__":
    path = "data/fr_ftb-ud-dev.conllu"
    
    children = children_per_branch(parse_tree_conll(path))
    print(children.keys())
    print(children['root'])
