#!/bin/sh

for numCores in 16 17 18 19 20
do
    echo "Using $numCores cores:"
    for i in 1 2 3
    do
        echo "Trial $i:"
        time ./all_in_one.py -c $numCores
    done
done
