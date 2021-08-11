#!/bin/sh
python3 extractor-new-new.py -D pickled-adjlist-maxed-files/ -w -c 4
python3 extractor-new-new.py -D pickled-adjlist-summed-files/ -w -c 4
python3 extractor-new-new.py -D pickled-adjlist-summed-files/ -d -w -c 4
python3 forest.py pickled-features-files/