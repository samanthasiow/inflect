#!/bin/bash

for prefix in train dtest etest; do
  for suffix in form tag lemma tree; do
    ln -s ~mpost/data/en600.468/generate/data/$prefix.$suffix data/$prefix.$suffix
  done
done
