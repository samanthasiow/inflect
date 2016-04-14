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

def inflections(lemma, lemmas):
    if lemmas.has_key(lemma):
        return sorted(lemmas[lemma].keys(), lambda x,y: cmp(lemmas[lemma][y], lemmas[lemma][x]))
    return [lemma]

def best_inflection(lemma, lemmas):
    return inflections(lemma, lemmas)[0]

if __name__ == '__main__':

    # Build a simple unigram model on the training data
    UNIGRAM_LEMMAS = defaultdict(defaultdict)
    BIGRAM_LEMMAS = defaultdict(defaultdict)
    if args.t:
        # combine creates the test file names = e.g. train.lemma, and train.form
        def combine(a, b): return '%s.%s' % (a, b)
        def utf8read(file): return codecs.open(file, 'r', 'utf-8')
        # Build the UNIGRAM_LEMMAS hash, a two-level dictionary mapping lemmas to inflections to counts
        # combine 'words' from train.form, and 'lemmas' from train.lemma
        for words, lemmas in izip(utf8read(combine(args.t, args.w)), utf8read(combine(args.t, args.l))):
            # print 'words from train.form: ', words
            # print 'lemmas from train.lemma: ', lemmas
            lemmas_array = lemmas.rstrip().lower().split()
            words_array = words.rstrip().lower().split()
            for i,word in enumerate(words_array):
                # might have an out of bounds error if len(lemmas) < len(words)
                lemma = lemmas_array[i]
                # print '\t', 'word: ', word, ', lemma:', lemma
                UNIGRAM_LEMMAS[lemma][word] = UNIGRAM_LEMMAS[lemma].get(word,0) + 1
                if i < len(words_array)-1:
                    lemma_bigram = (lemma, lemmas_array[i+1])
                    inflection_bigram = (word, words_array[i+1])
                    BIGRAM_LEMMAS[lemma_bigram][inflection_bigram] = BIGRAM_LEMMAS[lemma_bigram].get(inflection_bigram,0) + 1

        # for lemma in BIGRAM_LEMMAS:
            # print 'Lemma:' , lemma, ', inflections: ', BIGRAM_LEMMAS[lemma]

    # Choose the most common inflection for each word and output them as a sentence
    for line in sys.stdin:
        # check i,i+1 for bigram:
        # if doesn't exist:
            # check i for unigram:
            # i += 1
        # skip i+1, move to i=i+2

        idx = 0
        lemmas = line.rstrip().split()
        inflection_hyp = []
        while idx < len(lemmas):
            if idx < len(lemmas)-1:
                bigram = (lemmas[idx],lemmas[idx+1])
                if bigram in BIGRAM_LEMMAS:
                    best_bigram_inflection = best_inflection(bigram, BIGRAM_LEMMAS)
                    inflection_hyp.append(best_bigram_inflection[0])
                    inflection_hyp.append(best_bigram_inflection[1])
                    idx += 2
                    continue
            best_unigram_inflection = best_inflection(lemmas[idx], UNIGRAM_LEMMAS)
            inflection_hyp.append(best_unigram_inflection)
            idx += 1

        print ' '.join(inflection_hyp)
