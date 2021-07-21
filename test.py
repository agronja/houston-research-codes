#!/usr/bin/env python3
import os
import sys
import pprint
import gzip
import pickle
import networkx as nx
from multiprocessing import Pool
import progressbar
from tqdm import tqdm
import time

def printFiles(filename):
	time.sleep(0.5)
	return filename

def uniqueSyscalls(filename):
    return [line.decode().strip().split()[2] for line in gzip.open("og_dataset_7000/" + filename, "r")]


def main():
	
	print(10**10)

if __name__ == '__main__':
	main()