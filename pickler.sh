#!/bin/sh
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -d
echo
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -w
echo
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -d -w
echo
time ./extractor-new-new.py -D pickled-adjlist-summed-files/
echo
time ./extractor-new-new.py -D pickled-adjlist-summed-files/ -d
echo
time ./extractor-new-new.py -D pickled-adjlist-summed-files/ -w
echo
time ./extractor-new-new.py -D pickled-adjlist-summed-files/ -d -w
echo
time ./forest.py pickled-features-files/