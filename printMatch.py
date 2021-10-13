#!/usr/bin/env python3
#
# getline3 example with a class to collect lines that have a pattern.
#

import getline3
import re
import sys

#
# for convenience
#
getline = getline3.getline
eprint = getline3.eprint
ewrite = getline3.ewrite

#
# A class to store all lines contains 'pattern' to 'self._lines'
# The input stream is stdin if 'file' is None.
#
class printMatch():
    def __init__(self, pattern, file):
        if file == None:
            file = '-'
        self._obj = getline(file)
        self._re = re.compile(pattern)
        self._lines = []
        #
        # Collect matching lines
        #
        self._obj.runLoop(self.processLine, False, 0)

    def processLine(self, p, line, *argv):
        line = p.chop(line)
        m = self._re.search(line)
        if m != None:
            self._lines.append('%-10s %s' % (m.group(0), line))
        return True

    def get(self):
        return self._lines

    def __del__(self):
        del self._obj


def usage():
    eprint('Usage: printMatch pattern [file]')
    sys.exit(1)

def main():
    if len(sys.argv) <= 1:
        usage()
    elif len(sys.argv) <= 2:
        file = None
    else:
        file = sys.argv[2]

    obj = printMatch(sys.argv[1], file)
    for line in obj.get():
        print(line)

if __name__ == '__main__':
    main()
