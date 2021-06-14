# README.md

To use grapher.py, please refer to the following:

    Usage: grapher.py [options] filename
    
    -o              Count connections between two different calls once per line
    -a  NAME        Append NAME to the output file (default: -output)
    -s              Use sum of weights as weight for edge (default: max weight per argument)
    -j              Save output as a .json file (default: .txt file)
    -g              Output the final graph (default: only outputs parsed dictionary)
    -n  NAME        Name to save the output as (default: <current file name>-output.txt)
    -D  DIR         Directory to save the output to (default: output-files/)
                    WARNING: If directory does not exist, it will create a new one with the inputted name
