#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Outputs a fully inflected version of a lemmatized test set (provided on STDIN).
If training data is provided, it will use a unigram model to select the form.
usage: cat LEMMA_FILE | python inflect
       [-t TRAINING_PREFIX] [-l LEMMA_SUFFIX] [-w WORD_SUFFIX]
"""

import argparse
import codecs
import sys
import os
from collections import defaultdict
from itertools import izip

PARSER = argparse.ArgumentParser(description="Inflect a lemmatized corpus")
PARSER.add_argument("-t", type=str, default="data/train", help="training data prefix")
PARSER.add_argument("-l", type=str, default="lemma", help="lemma file suffix")
PARSER.add_argument("-w", type=str, default="form", help="word file suffix")
PARSER.add_argument("-d", type=str, default="data/dtest", help="test file")
PARSER.add_argument("-p", type=str, default="tag", help="part of speech tag")
args = PARSER.parse_args()

# Python sucks at UTF-8
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

def inflections(lemma, lemmas, tag):
    if lemmas.has_key((lemma, tag)):
        return sorted(lemmas[(lemma, tag)].keys(), lambda x,y: cmp(lemmas[(lemma, tag)][y], lemmas[(lemma,tag)][x]))
    elif lemmas.has_key(lemma):
        return sorted(lemmas[lemma].keys(), lambda x,y: cmp(lemmas[lemma][y], lemmas[lemma][x]))
    return [lemma]

def best_inflection(lemma, lemmas, pos):
    return inflections(lemma, lemmas, pos)[0]

if __name__ == '__main__':

    # Build a simple unigram model on the training data
    LEMMAS = defaultdict(defaultdict)
    if args.t:
        # combine creates the test file names = e.g. train.lemma, and train.form
        def combine(a, b): return '%s.%s' % (a, b)
        def utf8read(file): return codecs.open(file, 'r', 'utf-8')
        # Build the UNIGRAM_LEMMAS hash, a two-level dictionary mapping lemmas to inflections to counts
        # combine 'words' from train.form, and 'lemmas' from train.lemma
        for words, lemmas, tags in izip(utf8read(combine(args.t, args.w)), utf8read(combine(args.t, args.l)), utf8read(combine(args.t, args.p))):
            # print 'words from train.form: ', words
            # print 'lemmas from train.lemma: ', lemmas
            lemmas_array = lemmas.rstrip().lower().split()
            words_array = words.rstrip().lower().split()
            tags_array = tags.rstrip().lower().split()
            for word, lemma, tag in izip(words_array, lemmas_array, tags_array):
                LEMMAS[(lemma,tag)][word] = LEMMAS[(tag, lemma)].get(word,0) + 1
                LEMMAS[lemma][word] = LEMMAS[lemma].get(word,0) + 1

        # for lemma in BIGRAM_LEMMAS:
            # print 'Lemma:' , lemma, ', inflections: ', BIGRAM_LEMMAS[lemma]

    inflection_hyp = []
    for words, lemmas, tags in izip(utf8read(combine(args.d, args.w)), utf8read(combine(args.d, args.l)), utf8read(combine(args.d, args.p))): 
        lemmas_array = lemmas.rstrip().lower().split()
        tags_array = tags.rstrip().lower().split()
        for (lemma, tag) in izip(lemmas_array, tags_array):
            inflection_hyp.append(best_inflection(lemma, LEMMAS, tag))
    print ' '.join(inflection_hyp)
