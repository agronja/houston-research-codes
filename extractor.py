#!/usr/bin/env python3
import os
import sys
import pprint
import pickle
import networkx as nx
from multiprocessing import Pool

familyData      = {'allaple': 1, 'browserfox': 2, 'klez': 3, 'mira': 4, 'multiplug': 5}
single_conn     = False
directed        = False
weighted        = False
use_sum         = False
directory       = "Dataset Sample/"
fileNo = 0
cores = 15

def usage(exitVal):
    print(f''' Usage: {os.path.basename(sys.argv[0])} [options]

    -o              Count connections between two different calls once per line
    -s              Use sum of weights as weight for edge (default: max weight per argument)
    -d              Use a directed graph (default: undirected)
    -w              Use a weighted graph (default: unweighted)
    -c [INT]        Controls how many cores the program uses (default: 15)
    
    ''')

def splitLine(line):
    line = line.split()
    phandle = int(line[1], base=16)
    syscall = line[2]
    args = [int(arg, 16) for arg in line[3:] if int(arg, 16) != 0]

    return syscall, phandle, args

def getParsedDict(calls_file):
    global single_conn
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

def getGraphDict(parse):
    global weighted
    global directed
    global use_sum
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
    global weighted
    global directory
    fdn = directory + filename
    fd = open(fdn, "r")
    parse = getParsedDict(fd)
    graph = getGraphDict(parse)
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
    fd.close()
    return adjList

def uniqueSyscalls():
    f = open("unique_syscalls.txt", "r")
    return [line.strip() for line in f.readlines()]

syscalls = uniqueSyscalls()

def familyClass(filename):
    fileData = filename.split('_')
    return familyData[fileData[0]]

def featureExtractor(adjList):
    global syscalls
    global directed
    graphToUse = nx.Graph
    if directed:
        graphToUse = nx.DiGraph
    G = nx.parse_multiline_adjlist(iter(adjList), create_using=graphToUse)
    pr = nx.pagerank(G)
    ec = nx.eigenvector_centrality(G, weight='weight')
    ac = nx.average_clustering(G, weight='weight')

    fv = []
    for call in syscalls: 
        fv.append(pr.get(call, 0))
    
    for call in syscalls:
        fv.append(ec.get(call, 0))
    
    fv.append(ac)
    return fv

def fileProcessor(filename):
    global fileNo
    global cores
    print(filename, fileNo)
    family = familyClass(filename)
    adjList = getAdjList(filename)
    features = featureExtractor(adjList)
    theTup = (family, features)
    fileNo += cores
    return theTup
    
def main():

    arguments   = sys.argv[1:]
    global single_conn
    global directed
    global weighted
    global use_sum
    global directory
    global cores

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

    p = Pool(cores)
    theResults = p.map(fileProcessor, os.listdir(directory))

    typePrint = "averaged"
    directPrint = "directed"
    weightPrint = "weighted"

    if use_sum:
        typePrint = "summed"
    if not directed:
        directPrint = "un" + directPrint
    if not weighted:
        weightPrint = "un" + weightPrint
    
    fp = "pickled-files/" +  typePrint + "-" + directPrint + "-" + weightPrint + ".p"

    print(f"results pickled to {fp}")
    pickle.dump(theResults, open(fp, "wb"))

    '''
    for item in theResults:
        families.append(item[0])
        fvs.append(item[1])
    
    fv_train, fv_test, fam_train, fam_test = train_test_split(fvs, families, test_size=0.25, random_state=randNum)

    
    clf = RandomForestClassifier(n_estimators=100, max_depth=3)
    clf.fit(fv_train, fam_train)
    print(clf.score(fv_test, fam_test))
    '''

if __name__ == '__main__':
    main()