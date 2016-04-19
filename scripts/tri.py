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
args = PARSER.parse_args()

# Python sucks at UTF-8
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

# combine creates the test file names = e.g. train.lemma, and train.form
def combine(a, b): return '%s.%s' % (a, b)
def combine3(a,b,c): return '%s.%s.%s' %(a,b,c)

def inflections(before_prev_lemma, prev_lemma, lemma, lemmas):
    if lemmas.has_key(combine3(before_prev_lemma,prev_lemma,lemma)):
        return sorted(lemmas[combine3(before_prev_lemma,prev_lemma,lemma)].keys(),
                      lambda x,y: cmp(lemmas[combine3(before_prev_lemma,prev_lemma,lemma)][y], lemmas[combine3(before_prev_lemma,prev_lemma,lemma)][x]))
    elif lemmas.has_key(combine(prev_lemma,lemma)):
        return sorted(lemmas[combine(prev_lemma,lemma)].keys(), lambda x,y: cmp(lemmas[combine(prev_lemma,lemma)][y], lemmas[combine(prev_lemma,lemma)][x]))
    elif lemmas.has_key(lemma):
        return sorted(lemmas[lemma].keys(), lambda x,y: cmp(lemmas[lemma][y], lemmas[lemma][x]))
    return [lemma]

def best_inflection(before_prev_lemma, prev_lemma, lemma, lemmas):
    return inflections(before_prev_lemma, prev_lemma, lemma, lemmas)[0]

if __name__ == '__main__':

    # Build a simple unigram model on the training data
    LEMMAS = defaultdict(defaultdict)
    if args.t:

        def utf8read(file): return codecs.open(file, 'r', 'utf-8')
        # Build the UNIGRAM_LEMMAS hash, a two-level dictionary mapping lemmas to inflections to counts
        # combine 'words' from train.form, and 'lemmas' from train.lemma
        for words, lemmas in izip(utf8read(combine(args.t, args.w)), utf8read(combine(args.t, args.l))):
            # print 'words from train.form: ', words
            # print 'lemmas from train.lemma: ', lemmas
            lemmas_array = lemmas.rstrip().lower().split()
            words_array = words.rstrip().lower().split()
            before_last = "<s>"
            last = "<s>"
            for word, lemma in izip(words_array, lemmas_array):
                LEMMAS[lemma][word] = LEMMAS[lemma].get(word, 0) + 1
                LEMMAS[combine(last, lemma)][word] = LEMMAS[combine(last, lemma)].get(word, 0) + 1
                LEMMAS[combine3(before_last, last, lemma)][word] = LEMMAS[combine3(before_last, last, lemma)].get(word, 0) + 1
                before_last = last
                last = lemma


    # Choose the most common inflection for each word and output them as a sentence
    for line in sys.stdin:
        idx = 0
        lemmas = line.rstrip().lower().split()
        inflection_hyp = []
        last = "<s>"
        before_last = "<s>"
        while idx < len(lemmas):
            inflection_hyp.append(best_inflection(before_last, last, lemmas[idx], LEMMAS))
            before_last = last
            last = lemmas[idx]
            idx += 1
        print ' '.join(inflection_hyp)

