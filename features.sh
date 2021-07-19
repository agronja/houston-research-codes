#!/bin/sh
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -sD og_dataset_7000/ 
echo
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -sD og_dataset_7000/ -d
echo
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -sD og_dataset_7000/ -w
echo
time ./extractor-new-new.py -D pickled-adjlist-maxed-files/ -sD og_dataset_7000/ -d -w
echo