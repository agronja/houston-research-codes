#!/usr/bin/env python3
import os
import sys
import pprint
import re
import json

def splitLine(line):
    line = line.split()
    syscall = line[2]

    return syscall

def main():
    directory = 'Dataset Sample'
    syscalls = {}
    out = open('unique_syscalls.txt', 'w')
    for filename in os.scandir(directory):
        fd = open(filename, "r")
        for line in fd:
            call = splitLine(line)
            try:
                syscalls[call]
            except KeyError:
                syscalls[call] = 0
                out.write(f"{call}\n")
        fd.close()
    out.close()
    
if __name__ == '__main__':
    main()