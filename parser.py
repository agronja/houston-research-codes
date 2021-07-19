#!/usr/bin/env python3
import os
import sys
import pprint
import pickle
from multiprocessing import Pool
import gzip
from tqdm import tqdm

single_conn     = False
use_sum         = False
directory       = "Dataset Sample/"
typePrint       = "maxed"
cores           = 10

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


def createAdjList(graph):
    adjList = []
    for s1 in graph.keys():
        if not graph[s1]:
            continue
        line = f'{s1} {len(graph[s1])}'
        adjList.append(line)
        for s2 in graph[s1].keys():
            line = s2 + " " + "{'weight': " + str(graph[s1][s2]) + "}"
            adjList.append(line)
    return adjList


def getAdjList(filename, fileNo):
    global cores
    global typePrint
    print(filename, fileNo)
    fdn = directory + filename
    fd = gzip.open(fdn, "r")
    parse = getParsedDict(fd)
    fd.close()
    graph = getGraphDict(parse)
    parse.clear()
    adjList = createAdjList(graph)
    graph.clear()
    nfp = "pickled-adjlist-" + typePrint + "-files/" + filename.split('.')[0] + ".p"
    
    pickle.dump(adjList, open(nfp, "wb"))
    return

def main():

    arguments   = sys.argv[1:]
    global single_conn
    global use_sum
    global directory
    global cores
    global typePrint

    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-o':
            single_conn = True
        elif argument == '-s':
            use_sum = True
            typePrint = "summed"
        elif argument == '-c':
            cores = int(arguments.pop(0))
        elif argument == '-D':
            directory = arguments.pop(0)
        elif argument == '-h':
            usage(0)
        else:
            usage(-1)
    
    # syscalls = uniqueSyscalls()

    print(f"\nCreating adjacency lists for files in {directory}...\n")
    p = Pool(cores)
    for _ in tqdm(p.imap_unordered(getAdjList, os.listdir(directory)), total=len(os.listdir(directory))):
        pass
    '''
    d = []
    for idx, filename in enumerate(os.listdir(directory)):
        d.append((filename, idx))
    p = Pool(cores)
    p.starmap(getAdjList, d)
    '''

if __name__ == '__main__':
    main()