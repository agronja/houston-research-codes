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
    
    -s                  Count connections between two different calls once per line
    -j                  Save output as a .json file (default: .txt file)
    -g                  Output the final graph (default: only outputs parsed dictionary)
    -n  NAME            Name to save the output as (default: <current file name>-output.txt)
    -D  DIR             Directory to save the output to (default: output-files/)
                        WARNING: If directory does not exist, it will create a new one with this name
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
            json.dump(theDict, out)
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
    parse_only      = True
    save_as_json    = False
    
    while arguments and arguments[0].startswith('-'):

        argument = arguments.pop(0)
        if argument == '-D':
            output_folder = arguments.pop(0) + '/'
        elif argument == '-s':
            single_conn = True
        elif argument == '-g':
            parse_only = False
        elif argument == '-n':
            out_name = arguments.pop(0)
        elif argument == '-j':
            save_as_json = True
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
        out_name = filename_split[-2] + '-output'
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
                    graph[call][dep] = graph[call].get(dep, 0) + parse[phandle][argument][call][dep]

    print_to_file(output_name, graph, save_as_json)

if __name__ == '__main__':
    main()