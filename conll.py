#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---- System libraries --------------------------------------------------------
import re

# ---- Third-party libraries ---------------------------------------------------
from conllu import parse
from conllu import parse_tree


def load_conll(path_to_file: str)->str:
    """
    Load a CoNLL file.
    Skip lines containing contractions. 
    Return file content as a single string.
    
    :param path_to_file: Path to the conll file
    :returns: the file content as a single string
    """
    with open(path_to_file, 'r') as conll:
        lines = [line for line in conll.readlines() 
                 if not re.search(r'\d+-\d+', line)]
    return ''.join(lines)


def parse_conll(path_to_file: str)->list:
    """
    Read a CoNLL file and return
    a list of sentences as TokenList objects
    (TokenList == linearly ordered list).
    
    :param path_to_file: Path to the conll file
    :returns: a list of sentences as TokenList objects
    """
    return parse(load_conll(path_to_file))


def parse_tree_conll(path_to_file: str)->list:
    """
    Read a CoNLL file and return
    a list of sentences as TokenTree objects
    (TokenTree == arborised hierarchal structures).
    
    :param path_to_file: Path to the conll file
    :returns: a list of sentences as TokenTree objects
    """
    return parse_tree(load_conll(path_to_file))
    

if __name__ == "__main__":
    path = "data/fr_ftb-ud-dev.conllu"
    
    # Load a CoNLL file
    corpus = load_conll(path)
    print(corpus[:100])
    
    # Parse a CoNLL file as TokenList objects
    corpus = parse_conll(path)
    print(corpus[1])
    
    # Parse a CoNLL file as TokenTree objects
    corpus = parse_tree_conll(path)
    print(corpus[1])