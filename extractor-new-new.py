#!/usr/bin/env python3
import os
import sys
import pprint
import pickle
import networkx as nx
from multiprocessing import Pool
import gzip

from networkx.classes import graph

graphType       = None
weighted        = None
directory       = "Dataset Sample/"
cores           = 15
syscalls        = set()

def usage(exitVal):
    print(f''' Usage: {os.path.basename(sys.argv[0])} [options]

    -d             Use a directed graph (default: undirected)
    -w             Use a weighted graph (default: unweighted)
    -D [DIRECTORY]  Source of input files (default: "Dataset Sample/")
    -c [INT]        Controls how many cores the program uses (default: 15)
    
    ''')

    exit(exitVal)

def splitLine(line):
    return line.split()[2]

def uniqueSyscalls():
    print("Gathering all unique system calls...")
    syscalls = set()
    for filename in os.scandir(directory):
        syscalls.update([line.decode().strip().split()[2] for line in gzip.open(filename, "r")])
    return syscalls

def familyClass(filename):
    fileData = filename.split('_')
    return fileData[0]


def featureExtractor(adjList, d=False):
    global syscalls
    global graphType
    global weighted
    G = nx.parse_multiline_adjlist(iter(adjList), create_using=graphType)
    pr = nx.pagerank(G)
    ec = nx.eigenvector_centrality(G, weight=weighted)
    cc = nx.clustering(G, weight=weighted)
    ac = nx.average_clustering(G, weight=weighted)

    fv = []
    for call in syscalls: 
        fv.append(pr.get(call, 0))
        fv.append(ec.get(call, 0))
        fv.append(cc.get(call, 0))
    
    fv.append(ac)
    return fv

def fileProcessor(filename, fileNo):
    print(filename, fileNo)
    family = familyClass(filename)
    adjList = pickle.load(open(directory + filename, "rb"))
    fv = featureExtractor(adjList)
    theTup = (family, fv)
    return theTup

def getTypePrint():
    global directory
    typePrint = directory.split("-")[2]
    return typePrint

def main():

    arguments   = sys.argv[1:]
    global graphType
    global weighted
    global directory
    global cores
    global syscalls

    dPrint = "undirected"
    wPrint = "unweighted"

    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-d':
            graphType = nx.DiGraph
            dPrint = "directed"
        elif argument == '-w':
            weighted = 'weight'
            wPrint = "weighted"
        elif argument == '-c':
            cores = int(arguments.pop(0))
        elif argument == '-D':
            directory = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(-1)
    
    syscalls = uniqueSyscalls()
    typePrint = getTypePrint()

    print("\nCreating feature vectors for files in directory...\n")
    d = []
    for idx, filename in enumerate(os.listdir(directory)):
        d.append((filename, idx))
    p = Pool(cores)
    theResults = p.map(fileProcessor, d)

    fp = "pickled-features-files/" + typePrint + "-" + dPrint + "-" + wPrint + ".p"
    print(f"results pickled to {fp}")
    pickle.dump(theResults, open(fp, "wb"))

    
if __name__ == '__main__':
    main()