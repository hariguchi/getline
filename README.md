# getline
Get a line from a stream

Usage:
```python
% cat prLine.py
#!/usr/bin/env python
#
# Usage: prLine.py [file]
#

import getline
import re
import sys

def main():
    #
    # Read from stdin if there are no arguments
    #
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = '-'

    #
    # 1. Instantiate 'getline' with input file 'file'
    # 2. Call the main loop runLoop()
    # 2.1. runLoop() reads a line from 'file', then passes it to the first
    #      parameter processLine() until reaching the end of file
    # 2.1. runLoop() strips white spaces if the second parameter is 'True'
    # 2.2. runLoop() does not strip white spaces if the  second parameter is 'False'
    # 2.3. processLine() receives all parameters from the 3rd
    #
    ins = getline.getline(file)
    ins.runLoop(processLine, False, 0)

#
# p:      instance of class 'getline'
# line:   the line to be processed
# argv[]: parameters passed from the p.runLoop()
#
def processLine(p, line, *argv):
    r = re.compile(r'[0-9]+')
    line = p.chop(line)
    m = r.search(line)
    if m != None:
        print line


if __name__ == '__main__':
```

Example:
```
% cat prLine.py | ./prLine.py
    if len(sys.argv) > 1:
        file = sys.argv[1]
    # 1. Instantiate 'getline' with input file 'file'
    # 2. Call the main loop runLoop()
    # 2.1. runLoop() reads a line from 'file', then passes it to the first
    # 2.1. runLoop() strips white spaces if the second parameter is 'True'
    # 2.2. runLoop() does not strip white spaces if the  second parameter is 'False'
    # 2.3. processLine() receives all parameters from the 3rd
    ins.runLoop(processLine, False, 0)
    r = re.compile(r'[0-9]+')
%
% ./prLine.py prLine.py
    if len(sys.argv) > 1:
        file = sys.argv[1]
    # 1. Instantiate 'getline' with input file 'file'
    # 2. Call the main loop runLoop()
    # 2.1. runLoop() reads a line from 'file', then passes it to the first
    # 2.1. runLoop() strips white spaces if the second parameter is 'True'
    # 2.2. runLoop() does not strip white spaces if the  second parameter is 'False'
    # 2.3. processLine() receives all parameters from the 3rd
    ins.runLoop(processLine, False, 0)
    r = re.compile(r'[0-9]+')
```
