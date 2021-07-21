#!/bin/sh

# Globals
DIRECTED=0
WEIGHTED=0

# Parse Command Line Options

while [ $# -gt 0 ]; do 
    case $1 in
        -d)             DIRECTED=1
        -w)             WEIGHTED=1
        *)              usage 1;;
    esac
    shift
done

mkdir tmp-files

if [ "$DIRECTED" -eq 1 ] && ["$WEIGHTED" -eq 1]; then
	./extractor-new-new.py -d -w -cF syscalls.p -D pickled-adjlist-maxed-files/ -sD tmp-files/
elif [ "$DIRECTED" -eq 1 ]; then
    ./extractor-new-new.py -d -cF syscalls.p -D pickled-adjlist-maxed-files/ -sD tmp-files/
elif [ "$WEIGHTED" -eq 1 ]; then
    ./extractor-new-new.py -w -cF syscalls.p -D pickled-adjlist-maxed-files/ -sD tmp-files/
else
    ./extractor-new-new.py -cF syscalls.p -D pickled-adjlist-maxed-files/ -sD tmp-files/
fi



rm -rf tmp-files