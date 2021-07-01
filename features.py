#!/usr/bin/env python3
import os
import sys
import pprint
import re
import json
import networkx as nx

def usage(exitVal, filename=""):
    print(f"Error: Incorrect usage")
    if exitVal == -2:
        print(f"File {filename} does not exist\n")
    print(f'Usage: {os.path.basename(sys.argv[0])} filename')
    exit(exitVal)

def getAdjList():
    pass

def main():

    f = open("unique_syscalls.txt", "r")
    calls = [line.strip() for line in f.readlines()]

    if len(sys.argv) < 2:
        usage(-1)
    filename = sys.argv[1]
    try:
        adj_file = open(filename, "rb")
    except FileNotFoundError:
        usage(-2, filename)
    
    G = nx.read_multiline_adjlist(adj_file, create_using=nx.DiGraph)
    
    # Get pagerank and append to feature vector:
    pr = nx.pagerank(G)

    fv = []
    for call in calls:
        fv.append(pr.get(call, 0))

    # Get average clustering value and append to feature vector:
    fv.append(nx.average_clustering(G, weight='weight'))

    # Get eigenvector centrality values and append all to feature vector:
    ec = nx.eigenvector_centrality(G, weight='weight')
    for call in calls:
        fv.append(ec.get(call, 0))
    print(fv)
    print(len(fv))
    


    

if __name__ == '__main__':
    main()