#!/usr/bin/env python3
import os
import sys
import pprint
import pickle
import networkx as nx
from multiprocessing import Pool
import gzip

single_conn     = False
undirected      = True
unweighted      = True
directed        = True
weighted        = True
use_sum         = False
directory       = "Dataset Sample/"
fileNo          = 0
cores           = 15
syscalls        = set()

def usage(exitVal):
    print(f''' Usage: {os.path.basename(sys.argv[0])} [options]

    -o              Count connections between two different calls once per line
    -s              Use sum of weights as weight for edge (default: max weight per argument)
    -d              Use only a directed graph (default: both)
    -w              Use only a weighted graph (default: both)
    -ud             Use only an undirected graph (default: both)
    -uw             Use only an unweighted graph (default: both)
    -D [DIRECTORY]  Source of input files (default: "Dataset Sample/")
    -c [INT]        Controls how many cores the program uses (default: 15)
    
    ''')

    exit(exitVal)

def splitLine(line, calls=False):
    line = line.split()
    syscall = line[2]
    if calls:
        return syscall
    phandle = int(line[1], base=16)
    args = [int(arg, 16) for arg in line[3:] if int(arg, 16) != 0]

    return syscall, phandle, args

def getParsedDict(calls_file):
    global single_conn
    parse = {}

    for line in calls_file:
        line = line.decode().strip()
        curr_deps = []
        syscall, phandle, args = splitLine(line)

        # Create a new dictionary entry for phandle if it does not yet exist
        parse[phandle] = parse.get(phandle, {})

        # Create a new dictionary entry for each argument if it does not yet exist
        for argument in args:
            parse[phandle][argument] = parse[phandle].get(argument, {})

            # Create new dictionary entry for syscall in argument if it does not yet exist
            parse[phandle][argument][syscall] = parse[phandle][argument].get(syscall, {})

            # Update each syscall with dependencies
            for key in parse[phandle][argument].keys():
                if key == syscall:
                    continue
                
                if not single_conn or not key in curr_deps:
                    parse[phandle][argument][key][syscall] = parse[phandle][argument][key].get(syscall, 0) + 1
                    curr_deps.append(key)        
    return parse

def getGraphDict(parse):
    global use_sum
    graph = {}

    for phandle in parse.keys():
        for argument in parse[phandle].keys():
            for call in parse[phandle][argument].keys():
                graph[call] = graph.get(call, {})

                for dep in parse[phandle][argument][call].keys():
                    if use_sum:
                        graph[call][dep] = graph[call].get(dep, 0) + parse[phandle][argument][call][dep]
                    else:
                        graph[call][dep] = max(graph[call].get(dep, 0), parse[phandle][argument][call][dep])

    return graph


def getDirected(graph):
    edges = []
    for syscall1 in graph.keys():
        for syscall2 in graph[syscall1].keys():
            edge = {syscall1, syscall2}
            if edge not in edges:
                edges.append(edge)
                continue

            # edge between these two system calls already exists
            if use_sum:
                graph[syscall1][syscall2] += graph[syscall2][syscall1]
            else:
                graph[syscall1][syscall2] = max(graph[syscall1][syscall2], graph[syscall2][syscall1])
            graph[syscall2].pop(syscall1)
    return graph

def createAdjList(graph, w=False):
    adjList = []
    for s1 in graph.keys():
        if not graph[s1]:
            continue
        line = f'{s1} {len(graph[s1])}'
        adjList.append(line)
        for s2 in graph[s1].keys():
            line = f'{s2}'
            if w:
                line = line + " {'weight':" + str(graph[s1][s2]) + "}"
            adjList.append(line)
    return adjList

def getAdjList(filename):
    global weighted
    global directory
    fdn = directory + filename
    fd = gzip.open(fdn, "r")
    parse = getParsedDict(fd)
    graph = getGraphDict(parse)
    parse.clear()
    dw = []
    duw = []
    udw = []
    uduw = []

    if directed and weighted:
        dw = createAdjList(graph, w=True)
    if directed and unweighted:
        duw = createAdjList(graph, w=False)

    graph = getDirected(graph)

    if undirected and weighted:
        udw = createAdjList(graph, w=True)
    if undirected and unweighted:
        uduw = createAdjList(graph, w=False)
    graph.clear()
    fd.close()

    return dw, duw, udw, uduw


def uniqueSyscalls():
    print("Gathering all unique system calls...")
    syscalls = set()
    for filename in os.scandir(directory):
        syscalls.update([splitLine(line.decode().strip(), calls=True) for line in gzip.open(filename, "r")])
    return syscalls

def familyClass(filename):
    fileData = filename.split('_')
    return fileData[0]


def featureExtractor(adjList, d=False):
    global syscalls
    graphToUse = nx.Graph
    if d:
        graphToUse = nx.DiGraph
    G = nx.parse_multiline_adjlist(iter(adjList), create_using=graphToUse)
    pr = nx.pagerank(G)
    ec = nx.eigenvector_centrality(G, weight='weight')
    cc = nx.clustering(G, weight='weight')
    ac = nx.average_clustering(G, weight='weight')

    fv = []
    for call in syscalls: 
        fv.append(pr.get(call, 0))
        fv.append(ec.get(call, 0))
        fv.append(cc.get(call, 0))
    
    fv.append(ac)
    return fv

def fileProcessor(filename):
    global fileNo
    global cores
    print(filename, fileNo)
    family = familyClass(filename)
    dw, duw, udw, uduw = getAdjList(filename)
    dwf = []
    duwf = []
    udwf = []
    uduwf = []
    if directed and weighted:
        dwf = featureExtractor(dw, d=True)
    if directed and unweighted:
        duwf = featureExtractor(duw, d=True)
    if undirected and weighted:
        udwf = featureExtractor(udw)
    if undirected and unweighted:
        uduwf = featureExtractor(uduw)
    theTup = (family, dwf, duwf, udwf, uduwf)
    fileNo += cores
    return theTup

def main():

    arguments   = sys.argv[1:]
    global single_conn
    global undirected
    global unweighted
    global directed
    global weighted
    global use_sum
    global directory
    global cores
    global syscalls

    typePrint = "maxed"

    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-o':
            single_conn = True
        elif argument == '-s':
            use_sum = True
            typePrint = "summed"
        elif argument == '-d':
            undirected = False
            directed = True
        elif argument == '-w':
            unweighted = False
            weighted = True
        elif argument == '-ud':
            directed = False
            undirected = True
        elif argument == '-uw':
            weighted = False
            unweighted = True
        elif argument == '-c':
            cores = int(arguments.pop(0))
        elif argument == '-D':
            directory = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(-1)
    
    syscalls = uniqueSyscalls()

    print("\nCreating feature vectors for files in directory...\n")
    p = Pool(cores)
    theResults = p.map(fileProcessor, os.listdir(directory))

    dw = []
    duw = []
    udw = []
    uduw = []

    for item in theResults:
        if directed and weighted:
            theTup = (item[0], item[1])
            dw.append(theTup)
        if directed and unweighted:
            theTup = (item[0], item[2])
            duw.append(theTup)
        if undirected and weighted:
            theTup = (item[0], item[3])
            udw.append(theTup)
        if undirected and unweighted:
            theTup = (item[0], item[4])
            uduw.append(theTup)

    if directed and weighted:
        fp = "new-pickled-files/" + typePrint + "-directed-weighted.p"
        pickle.dump(dw, open(fp, "wb"))
        print(f"Directed weighted results pickled to {fp}")
    if directed and unweighted:
        fp = "new-pickled-files/" + typePrint + "-directed-unweighted.p"
        pickle.dump(duw, open(fp, "wb"))
        print(f"Directed unweighted results pickled to {fp}")
    if undirected and weighted:
        fp = "new-pickled-files/" + typePrint + "-undirected-weighted.p"
        pickle.dump(udw, open(fp, "wb"))
        print(f"Undirected weighted results pickled to {fp}")
    if undirected and unweighted:
        fp = "new-pickled-files/" + typePrint + "-undirected-unweighted.p"
        pickle.dump(uduw, open(fp, "wb"))
        print(f"Undirected unweighted results pickled to {fp}")

if __name__ == '__main__':
    main()