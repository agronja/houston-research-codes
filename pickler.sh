#!/bin/sh
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -w -c 10
echo
time ./extractor-new-new.py -D pickled-adjlist-summed-files/ -w -c 10
echo
time ./extractor-new-new.py -D pickled-adjlist-summed-files/ -d -w -c 10
echo
time ./forest.py pickled-features-files/