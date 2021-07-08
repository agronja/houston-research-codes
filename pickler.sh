#!/bin/sh
echo "none: "
./all_in_one.py -s
echo
echo "directed: "
./all_in_one.py -d -s
echo
echo "weighted: "
./all_in_one.py -w -s
echo
echo "directed and weighted: "
./all_in_one.py -s -d -w -c 10
echo 