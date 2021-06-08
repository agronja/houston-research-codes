#!/usr/bin/env python3
import sys
import pprint
import re


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
    prev_line = []
    calls_file.close()

    while content:
        line = content[0].split()
        curr_phandle = int(line[1], base=16)
        curr_syscall = line[2]
        curr_args = [int(arg, 16) for arg in line[3:] if int(arg, 16) != 0]
        curr_line = [curr_syscall]
        '''
        for element in content[1:]:

            element = element.split()
            syscall = element[2]
            if syscall == curr_syscall:
                continue

            phandle = int(element[1], base=16)
            if phandle != curr_phandle:
                continue

            args = [int(arg, 16) for arg in element[3:] if int(arg, 16) != 0]
            if not set(args).intersection(curr_args):
                continue

            # There is a dependency between these two system calls
            curr_line.append(syscall)
        
        # Check if current line is equal to the previous line
        if prev_line == curr_line:
            continue
        else:
            prev_line = curr_line
            curr_line_str = " ".join(curr_line)
            print(curr_line_str, file=output_file)
        '''
        content.pop(0)
        pprint.pprint(content)

    output_file.close()

if __name__ == '__main__':
    main()