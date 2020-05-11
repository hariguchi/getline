# getline
The getline module provides a simple interface to read a line
from an input stream and pass it to the specified function. An
input stream can be a regular file, stdin, or pipe. 

## Usage
```python
import getline
import re

def main():
    #
    # 1. Instantiate getline object.
    #    The parameter specifies an input stream
    #
    f = getline.getline('/etc/passwd') # regular file
    s = getline.getline('-')           # stdin
    p = getline.getline('ls /etc |')   # pipe

    #
    # 2. Call getline.runLoop() that reads input stream
    #    param 1:  function to be called each time a new line is read
    #              (let us call it processLine())
    #    param 2:  line is stripped if it is True
    #              line is *NOT* stripped if is False
    #    param 3-: all parameters from the 3rd are passed to processLine()
    #
    #    Return value:
    #     True:  input stream reached EOF (end of file)
    #     False: processLine() exited before the input stream reached EOF
    #
    rc = p.runLoop(processLine, False, 0)
    if rc == True:
        print '*** Reached the end of file ***'
    else:
        print '*** Quit before reaching the end of file ***'

    #
    # 3. destruct the getline object
    #
    del p
    del f
    del s


#
# processLine():
#  param 1:  pointer to the getline object
#  param 2:  line to be processed
#  param 3-: passed from p.runLoop()
#
#  Return value:
#    True:  p.runLoop() to continue to read lines
#    False: p.runLoop() to stop reading lines and return False
#
def processLine(p, line, *argv):
    r = re.compile(r'[0-9]+')
    line = p.chop(line)
    m = r.search(line)
    if m != None:
        print line

    return True

if __name__ == '__main__':
    main()
```

## How to test the module
```shell
  python -m unittest -v getline
```
