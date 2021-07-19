#!/usr/bin/env python3
import os
import sys
import pprint
import pickle
import networkx as nx
from multiprocessing import Pool
import gzip
import progressbar
from tqdm import tqdm

from networkx.classes import graph

graphType       = None
weighted        = None
callDirectory   = "og_dataset_7000/"
directory       = "pickled-adjlist-maxed-files/"
cores           = 15
syscalls        = set()

def usage(exitVal):
    print(f''' Usage: {os.path.basename(sys.argv[0])} [options]

    -d              Use a directed graph (default: undirected)
    -w              Use a weighted graph (default: unweighted)
    -D [DIRECTORY]  Source of input files (default: "Dataset Sample/")
    -sD [DIRECTORY] Source of system calls (defualt: "Dataset Sample/")
    -c [INT]        Controls how many cores the program uses (default: 15)
    
    ''')

    exit(exitVal)

def splitLine(line):
    return line.split()[2]

def uniqueSyscalls(filename):
    return [line.decode().strip().split()[2] for line in gzip.open(callDirectory + filename, "r")]

def familyClass(filename):
    fileData = filename.split('_')
    return fileData[0]


def featureExtractor(adjList):
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

def fileProcessor(filename):
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
    global callDirectory
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
        elif argument == '-sD':
            callDirectory = arguments.pop(0)
        elif argument == '-D':
            directory = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(-1)

    tPrint = "Going to create a " + dPrint + " " + wPrint + " graph"
    print(tPrint)

    print("\nGathering all unique system calls...\n")
    pd = Pool(cores)
    for x in tqdm(pd.imap_unordered(uniqueSyscalls, os.listdir(callDirectory)), total=len(os.listdir(callDirectory))):
        syscalls.update(x)
    print(f"\nNumber of system calls: {len(syscalls)}")

    typePrint = getTypePrint()

    print("\nCreating feature vectors for files in directory...\n")
    p = Pool(cores)
    theResults = []
    for x in tqdm(p.imap_unordered(fileProcessor, os.listdir(directory)), total=len(os.listdir(directory))):
        theResults.append(x)

    fp = "pickled-features-files/" + typePrint + "-" + dPrint + "-" + wPrint + ".p"
    print(f"\nresults pickled to {fp}\n")
    pickle.dump(theResults, open(fp, "wb"))

    
if __name__ == '__main__':
    main()