#!/usr/bin/env python3
from itertools import compress
import os
import sys
import pprint
import networkx as nx
from multiprocessing import Pool

familyData      = {'allaple': 1, 'browserfox': 2, 'klez': 3, 'mira': 4, 'multiplug': 5}
single_conn     = False
directed        = False
weighted        = False
use_sum         = False
directory       = "Dataset Sample/"

def usage(exitVal):
    print(f''' Usage: {os.path.basename(sys.argv[0])} [options]

    -o              Count connections between two different calls once per line
    -s              Use sum of weights as weight for edge (default: max weight per argument)
    -d              Use a directed graph (default: undirected)
    -w              Use a weighted graph (default: unweighted)
    
    ''')

def splitLine(line):
    line = line.split()
    phandle = int(line[1], base=16)
    syscall = line[2]
    args = [int(arg, 16) for arg in line[3:] if int(arg, 16) != 0]

    return syscall, phandle, args

def getParsedDict(calls_file, single_conn):
    parse = {}

    line = calls_file.readline()
    while line:
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

        line = calls_file.readline()
    return parse

def getGraphDict(parse, weighted, use_sum, directed):
    graph = {}

    for phandle in parse.keys():
        for argument in parse[phandle].keys():
            for call in parse[phandle][argument].keys():
                graph[call] = graph.get(call, {})

                for dep in parse[phandle][argument][call].keys():
                    if not weighted:
                        graph[call][dep] = 1
                    elif use_sum:
                        graph[call][dep] = graph[call].get(dep, 0) + parse[phandle][argument][call][dep]
                    else:
                        graph[call][dep] = max(graph[call].get(dep, 0), parse[phandle][argument][call][dep])
    if not directed:
        edges = []
        for syscall1 in graph.keys():
            for syscall2 in graph[syscall1].keys():
                edge = {syscall1, syscall2}
                if edge not in edges:
                    edges.append(edge)
                    continue

                # edge between these two system calls already exists
                if not weighted:
                    graph[syscall1][syscall2] = 1
                elif use_sum:
                    graph[syscall1][syscall2] += graph[syscall2][syscall1]
                else:
                    graph[syscall1][syscall2] = max(graph[syscall1][syscall2], graph[syscall2][syscall1])
                graph[syscall2].pop(syscall1)
    return graph

def getAdjList(filename):
    global single_conn
    global directed
    global weighted
    global use_sum
    global directory
    fdn = directory + filename
    fd = open(fdn, "r")
    parse = getParsedDict(fd, single_conn)
    graph = getGraphDict(parse, weighted, use_sum, directed)
    parse.clear()
    adjList = []
    for s1 in graph.keys():
        if not graph[s1]:
            continue
        line = f'{s1} {len(graph[s1])}'
        adjList.append(line)
        for s2 in graph[s1].keys():
            line = f'{s2}'
            if weighted:
                line = line + " {'weight':" + str(graph[s1][s2]) + "}"
            adjList.append(line)
    graph.clear()
    return adjList

def uniqueSyscalls():
    f = open("unique_syscalls.txt", "r")
    return [line.strip() for line in f.readlines()]

def familyClass(filename):
    fileData = filename.split('_')
    return familyData[fileData[0]]

def featureExtractor(adjList, calls):
    G = nx.parse_multiline_adjlist(iter(adjList))
    pr = nx.pagerank(G)
    ec = nx.eigenvector_centrality(G, weight='weight')
    ac = nx.average_clustering(G, weight='weight')

    fv = []
    for call in calls: 
        fv.append(pr.get(call, 0))
    
    for call in calls:
        fv.append(ec.get(call, 0))
    
    fv.append(ac)
    return fv

def fileProcessor(filename, calls):
    family = familyClass(filename)
    adjList = getAdjList(filename)
    features = featureExtractor(adjList, calls)
    theTup = (family, features)
    return theTup
    
def main():

    arguments   = sys.argv[1:]
    global single_conn
    global directed
    global weighted
    global use_sum
    global directory
    cores       = 12
    families    = []
    fvs         = []

    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-o':
            single_conn = True
        elif argument == '-s':
            use_sum = True
        elif argument == '-d':
            directed = True
        elif argument == '-w':
            weighted = True
        elif argument == '-c':
            cores = int(arguments.pop(0))
        elif argument == '-h':
            usage(0)
        else:
            usage(-1)

    syscalls    = uniqueSyscalls()
    args = []

    for filename in os.listdir(directory):
        farg = (filename, syscalls)
        args.append(farg)
    p = Pool(cores)
    theResults = p.starmap(fileProcessor, args)
    for item in theResults:
        families.append(item[0])
        fvs.append(item[1])
    print(fvs)
    print(families)

if __name__ == '__main__':
    main()