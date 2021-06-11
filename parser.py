#!/usr/bin/env python3
import sys
import pprint
import re
import concurrent.futures

curr_syscall = ''
curr_phandle = 0
curr_args = []

def flatten(sequence):
    for iterable in sequence:
        yield from iterable

def sortLine(line):
    line = line.split()
    phandle = int(line[1], base=16)
    syscall = line[2]
    args = [int(arg, 16) for arg in line[3:] if int(arg, 16) != 0]

    return syscall, phandle, args

def yieldLine(line):
    line = line.split()
    phandle = int(line[1], base=16)
    syscall = line[2]
    args = [int(arg, 16) for arg in line[3:] if int(arg, 16) != 0]

    yield phandle, syscall, args

def func1(syscall, phandle, args):
    global curr_syscall, curr_phandle, curr_args
    if syscall != curr_syscall and phandle == curr_phandle and set(args).intersection(curr_args):
        return[syscall]
    return []

def func2(arguments):
    return func1(*arguments)

def findDep(curr_sys, curr_phandle, curr_args, content, cores=8):
    print("A")
    arguments = (yieldLine(line) for line in content)

    with concurrent.futures.ProcessPoolExecutor(cores) as executor:
        results = executor.map(func2, arguments)
        results = flatten(results)
    
    return results

def main():
    if len(sys.argv) != 2:
        print("Error: Incorrect command line argument\nUsage: ./parser.py <filename>")
        exit(-1)
    
    filename = sys.argv[1]

    calls_file = open(filename, "r")
    filename_split = re.split('/|\.', filename)
    output_name = 'output-files/' + filename_split[1] + '-parsed-output.' + filename_split[2]

    output_file = open(output_name, "w")
    
    content = calls_file.readlines()
    prev_line = ""
    calls_file.close()

    while content:
        print("B")
        line = content.pop(0)
        syscall, phandle, args = sortLine(line)
        global curr_syscall, curr_phandle, curr_args
        curr_syscall = syscall
        curr_phandle = phandle
        curr_args = args


        curr_line = findDep(curr_syscall, curr_phandle, curr_args, content)
        curr_string = " ".join(curr_line)
        if curr_string == prev_line:
            continue
        
        prev_line = curr_string
        print(curr_string, file=output_file)

    output_file.close()

if __name__ == '__main__':
    main()