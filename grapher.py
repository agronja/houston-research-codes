#!/usr/bin/env python3
import os
import sys
import pprint
import re
import json

def usage(exitVal, filename=""):
    print(f"Error: Incorrect usage")
    if exitVal == -2:
        print(f"File {filename} does not exist\n")
    print(f'''Usage: {os.path.basename(sys.argv[0])} [options] filename
    
    -o              Count connections between two different calls once per line
    -a  NAME        Append NAME to the output file (default: -output)
    -s              Use sum of weights as weight for edge (default: max weight per argument)
    -j              Save output as a .json file (default: .txt file)
    -p              Output the parsed dictionary (default: outputs the adjacency list)
    -g              Output a human-readable graph (default: outputs the adjacency list)
    -adj            Output an undirected, unweighted multiline adjacency list
    -ud             Output a undirected multiline adjacency list (NOTE: only works with -adj flag)
    -uw             Output a unweighted miltiline adjacency list (NOTE: only works with -adj flag)
    -n  NAME        Name to save the output as (default: <current file name>-output.txt)
    -D  DIR         Directory to save the output to (default: output-files/)
                    WARNING: If directory does not exist, it will create a new one with the inputted name
    ''')
    exit(exitVal)

def splitLine(line):
    line = line.split()
    phandle = int(line[1], base=16)
    syscall = line[2]
    args = [int(arg, 16) for arg in line[3:] if int(arg, 16) != 0]

    return syscall, phandle, args

def print_to_file(filename, theDict, asJson):
    with open(filename, 'w') as out:
        if asJson:
            json.dump(theDict, out, indent=4)
        else:
            pprint.pprint(theDict, stream=out)
    exit(0)

def main():
    if len(sys.argv) < 2:
        usage(-1)
    
    arguments       = sys.argv[1:]
    output_folder   = 'output-files/'
    out_name        = False
    single_conn     = False
    parse_only      = False
    graph_only      = False
    save_as_json    = False
    use_sum         = False
    undirected      = False
    unweighted      = False
    append          = "-output"
    
    while arguments and arguments[0].startswith('-'):

        argument = arguments.pop(0)
        if argument == '-D':
            output_folder = arguments.pop(0) + '/'
        elif argument == '-o':
            single_conn = True
        elif argument == '-p':
            parse_only = True
        elif argument == '-g':
            graph_only = True
        elif argument == '-n':
            out_name = arguments.pop(0)
        elif argument == '-j':
            save_as_json = True
        elif argument == '-s':
            use_sum = True
        elif argument == '-a':
            append = arguments.pop(0)
        elif argument == '-adj':
            adj_list = True
        elif argument == '-ud':
            undirected = True
        elif argument == '-uw':
            unweighted = True
        elif argument == '-h':
            usage(0)
        else:
            usage(-1)
    
    filename = sys.argv[-1]

    try:
        calls_file = open(filename, "r")
    except FileNotFoundError:
        usage(-2, filename)
    filename_split = re.split('/|\.', filename)
    if not out_name:
        out_name = filename_split[-2] + append
    out_end = '.txt'
    if save_as_json:
        out_end = '.json'
    output_name = output_folder + out_name + out_end

    
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
    
    calls_file.close()
    if parse_only:
        print_to_file(output_name, parse, save_as_json)
    
    graph = {}

    for phandle in parse.keys():
        for argument in parse[phandle].keys():
            for call in parse[phandle][argument].keys():
                graph[call] = graph.get(call, {})

                for dep in parse[phandle][argument][call].keys():
                    if unweighted:
                        graph[call][dep] = 1
                    elif use_sum:
                        graph[call][dep] = graph[call].get(dep, 0) + parse[phandle][argument][call][dep]
                    else:
                        graph[call][dep] = max(graph[call].get(dep, 0), parse[phandle][argument][call][dep])

    parse.clear()
    
    if undirected:
        edges = []
        for syscall1 in graph.keys():
            for syscall2 in graph[syscall1].keys():
                edge = {syscall1, syscall2}
                if edge not in edges:
                    edges.append(edge)
                    continue

                # edge between these two system calls already exists
                if unweighted:
                    graph[syscall1][syscall2] = 1
                elif use_sum:
                    graph[syscall1][syscall2] += graph[syscall2][syscall1]
                else:
                    graph[syscall1][syscall2] = max(graph[syscall1][syscall2], graph[syscall2][syscall1])
                graph[syscall2].pop(syscall1)

    if graph_only:
        print_to_file(output_name, graph, save_as_json)

    newline = False
    f = open(output_name, "w")
    for s1 in graph.keys():
        if not graph[s1]:
            continue
        if newline:
            f.write('\n')
        newline = True
        f.write(f'{s1} {len(graph[s1])}')
        for s2 in graph[s1].keys():
            f.write(f'\n{s2}')
            if not unweighted:
                writeLine = " {'weight':" + str(graph[s1][s2]) + "}"
                f.write(writeLine)


if __name__ == '__main__':
    main()