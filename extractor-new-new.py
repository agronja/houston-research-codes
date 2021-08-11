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

directed        = False
weighted        = None
callFile        = "syscalls.p"
directory       = "pickled-adjlist-maxed-files/"
pickleDirectory = "tmp-files/"
cores           = 10
syscalls        = set()
numFiles        = 0

def usage(exitVal):
    print(f''' Usage: {os.path.basename(sys.argv[0])} [options]

    -d              Use a directed graph (default: undirected)
    -w              Use a weighted graph (default: unweighted)
    -D [DIRECTORY]  Source of input files (default: "pickled-adjlist-maxed-files/")
    -cF [FILE]      Source of pickled unique system calls (default: "syscalls.p")
    -sD [DIRECTORY] Where to save feature files (default: "tmp-files")
    -c [INT]        Controls how many cores the program uses (default: 10)
    
    ''')

    exit(exitVal)

def splitLine(line):
    return line.split()[2]
'''
def uniqueSyscalls(filename):
    return [line.decode().strip().split()[2] for line in gzip.open(callDirectory + filename, "r")]
'''
def familyClass(filename):
    fileData = filename.split('_')
    return fileData[0]


def featureExtractor(adjList):
    global syscalls
    global directed
    global weighted
    graphType = None
    if directed:
        graphType = nx.DiGraph
    G = nx.parse_multiline_adjlist(iter(adjList), create_using=graphType)
    pr = nx.pagerank(G)
    cc = nx.clustering(G, weight=weighted)
    ac = nx.average_clustering(G, weight=weighted)

    fv = []
    for call in syscalls: 
        fv.append(pr.get(call, 0))
        fv.append(cc.get(call, 0))
        try:
            fv.append(G.degree[call])
        except KeyError:
            fv.append(0)
    
    fv.append(ac)
    return fv

def fileProcessor(filename, idx):
    
    global numFiles
    print(f"Files processed: {numFiles:6}, Most recent file: {idx:6}")
    numFiles += 1
    
    family = filename.split('_')[0]
    adjList = pickle.load(open(directory + filename, "rb"))
    
    fv = featureExtractor(adjList)
    
    #if numFiles == (len(os.listdir(directory))//cores):
    #    print("A thread has finished.")

    return (family, fv)

def getTypePrint():
    global directory
    typePrint = directory.split("-")[2]
    return typePrint

def main():

    arguments   = sys.argv[1:]
    global directed
    global weighted
    global directory
    global callFile
    global cores
    global syscalls

    dPrint = "undirected"
    wPrint = "unweighted"

    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-d':
            directed = True
            dPrint = "directed"
        elif argument == '-w':
            weighted = 'weight'
            wPrint = "weighted"
        elif argument == '-c':
            cores = int(arguments.pop(0))
        elif argument == '-cF':
            callFile = arguments.pop(0)
        elif argument == '-D':
            directory = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(-1)

    tPrint = "Creating a " + dPrint + " " + wPrint + " graph..."
    print(tPrint)

    print("\nGathering all unique system calls...")
    syscalls = pickle.load(open(callFile, "rb"))
    '''
    p = Pool(cores)
    for x in tqdm(p.imap_unordered(uniqueSyscalls, os.listdir(callDirectory)), total=len(os.listdir(callDirectory))):
        syscalls.update(x)
    print(f"\nNumber of system calls: {len(syscalls)}")

    p.close()
    '''
    typePrint = getTypePrint()
    d = []
    for idx, filename in enumerate(os.listdir(directory)):
        d.append((filename, idx))
    
    sys.setrecursionlimit(10**9)
    print("\nCreating feature vectors for files in directory...\n")
    p = Pool(cores)
    '''
    theResults = []
    
    widgets = ['Files Processed: ', progressbar.Percentage(), ' [', progressbar.Timer(), '] ', progressbar.Bar(left='[', right=']'), ' (', progressbar.ETA(), ') ',]
    bar = progressbar.ProgressBar(widgets=widgets).start()
    for file in bar(os.listdir(directory)):
        theResults.append(fileProcessor(file))
    bar.finish()
    
    for x in tqdm(p.imap_unordered(fileProcessor, os.listdir(directory)), total=len(os.listdir(directory))):
        theResults.append(x)
    '''
    theResults = p.starmap(fileProcessor, d)
    
    # p.close()
    fp = "pickled-final-files/" + typePrint + "-" + dPrint + "-" + wPrint + ".p"
    pickle.dump(theResults, open(fp, "wb"))
    print(f"Results pickled to {fp}")


    
if __name__ == '__main__':
    main()