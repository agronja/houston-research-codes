#!/bin/sh
time ./parser.py -D og_dataset_7000/ -o
echo
time ./parser.py -D og_dataset_7000/ -s -o
echo
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/
echo
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -d
echo
time ./extractor-new-new.py -D pickled-adjlist-summed-files/ -w
echo
time ./extractor-new-new.py -D pickled-adjlist-summed-files/ -d -w
echo