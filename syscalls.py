#!/usr/bin/env python3
import os
import random
from multiprocessing import Pool
from tqdm import tqdm
import gzip
import pickle

def uniqueSyscalls(filename):
    return[line.decode().strip().split()[2] for line in gzip.open("og_dataset_7000/" + filename, "r")]

def main():
    directory = 'og_dataset_7000/'
    syscalls = set()
    p = Pool(15)
    for x in tqdm(p.imap_unordered(uniqueSyscalls, os.listdir(directory)), total=len(os.listdir(directory))):
        syscalls.update(x)
    p.close()
    pickle.dump(syscalls, open("sys-tmp/syscalls.p", "wb"))

if __name__ == '__main__':
    main()