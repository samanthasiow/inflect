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
    TRIGRAM_LEMMAS = defaultdict(defaultdict)
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
                lemma = lemmas_array[i]
                UNIGRAM_LEMMAS[lemma][word] = UNIGRAM_LEMMAS[lemma].get(word,0) + 1
                # get bigram
                if i < len(words_array)-1:
                    lemma_bigram = (lemma, lemmas_array[i+1])
                    inflection_bigram = (word, words_array[i+1])
                    BIGRAM_LEMMAS[lemma_bigram][inflection_bigram] = BIGRAM_LEMMAS[lemma_bigram].get(inflection_bigram,0) + 1
                # get trigram
                if i < len(words_array)-2:
                    lemma_bigram = (lemma, lemmas_array[i+1], lemmas_array[i+2])
                    inflection_bigram = (word, words_array[i+1], words_array[i+2])
                    TRIGRAM_LEMMAS[lemma_bigram][inflection_bigram] = TRIGRAM_LEMMAS[lemma_bigram].get(inflection_bigram,0) + 1

    # Choose the most common inflection for each word and output them as a sentence
    for line in sys.stdin:

        idx = 0
        lemmas = line.rstrip().split()
        inflection_hyp = []
        while idx < len(lemmas):
            # check trigram
            if idx < len(lemmas)-2:
                trigram = (lemmas[idx],lemmas[idx+1],lemmas[idx+2])
                if trigram in TRIGRAM_LEMMAS:
                    best_trigram_inflection = best_inflection(trigram, TRIGRAM_LEMMAS)
                    inflection_hyp.append(best_trigram_inflection[0])
                    inflection_hyp.append(best_trigram_inflection[1])
                    idx += 3
                    continue
            # check bigram if !trigram
            if idx < len(lemmas)-1:
                bigram = (lemmas[idx],lemmas[idx+1])
                if bigram in BIGRAM_LEMMAS:
                    best_bigram_inflection = best_inflection(bigram, BIGRAM_LEMMAS)
                    inflection_hyp.append(best_bigram_inflection[0])
                    inflection_hyp.append(best_bigram_inflection[1])
                    idx += 2
                    continue
            # check unigram if !bigram
            best_unigram_inflection = best_inflection(lemmas[idx], UNIGRAM_LEMMAS)
            inflection_hyp.append(best_unigram_inflection)
            idx += 1

        print ' '.join(inflection_hyp)
