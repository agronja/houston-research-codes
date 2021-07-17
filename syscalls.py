#!/usr/bin/env python3
import os
import random

def splitLine(line):
    line = line.split()
    syscall = line[2]

    return syscall

def main():
    directory = 'Dataset Sample/'
    syscalls = set()
    out = open('unique_syscalls.txt', 'w')
    for filename in os.scandir(directory):
        syscalls.update([splitLine(line) for line in open(filename, "r")])
        print(len(syscalls))
    print(syscalls)
    out.close()
    '''
    for filename in os.scandir(directory):
        fd = open(filename, "r")
        for line in fd:
            call = splitLine(line)
            try:
                syscalls[call]
            except KeyError:
                syscalls[call] = 0
        fd.close()
    calls = list(syscalls.keys())
    random.shuffle(calls)
    for call in calls:
        out.write(f"{call}\n")
    out.close()
    '''

if __name__ == '__main__':
    main()