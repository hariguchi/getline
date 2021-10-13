r''' getline3 - Get each line from a stream 

   Copyright (c) 2021 Yoichi Hariguchi
   All rights reserved.

   Permission to use, copy, modify, and distribute this software for any
   purpose with or without fee is hereby granted, provided that the above
   copyright notice and this permission notice appear in all copies.

   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
   WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
   MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
   ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
   WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
   ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
   OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


The getline module provides a simple interface to read a line from an input
stream and pass it to the specified function. An input stream can be a
regular file, stdin, or pipe.

Bonus: This module has the functions that print out a string to stderr.

  - eprint(*args, **kwargs)
  - ewrite(string)

You can use them like as follows:

  import getline3
  getline = getline3.getline
  eprint = getline3.eprint
  ewrite = getline3.ewrite

  eprint('ERROR:')

eprint() adds a newline at the end while ewrite() does not.


Example:

import getline3
import re

getline = getline3.getline
eprint = getline3.eprint
ewrite = getline3.ewrite

def main():
    #
    # 1. Instantiate getline object
    #    The parameter specifies an input stream
    #
    f = getline('/etc/passwd') # regular file
    s = getline('-')           # stdin
    p = getline('ls /etc |')   # pipe

    #
    # 2.1. Get the file descriptor associated with the input stream 
    #
    fd = p.fd()

    #
    # 2.2. runLoop() reads input stream line by line:
    #      param 1:  function to be called each time a new line is read
    #                (processLine() in this example)
    #      param 2:  True:  line is stripped
    #                False: line is *NOT* stripped
    #      param 3-: all parameters from the 3rd are passed to processLine()
    #
    #      Return value:
    #       True:  input stream reached EOF (end of file)
    #       False: runLoop() exited before the input stream reached EOF
    #
    rc = p.runLoop(processLine, False, 0)
    if rc == True:
        print('*** Reached the end of file ***')
    else:
        print('*** Quit before reaching the end of file ***')

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
    r = re.compile(r' ([0-9]+) ')
    line = p.chop(line)
    m = r.search(line)
    if m != None:
        print(m.group(1))

    return True

if __name__ == '__main__':
    main()


How to test the module:
  python3 -m unittest -v getline3
'''

import os
import re
import shlex
import subprocess
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def ewrite(str):
    sys.stderr.write(str)
    sys.stderr.flush()



class getline:
    def __init__(self, file):
        self._fd = None
        self._pipe = None

        file = file.strip()
        if file == '-':
            self._fd = sys.stdin
        else:
            if file[len(file) - 1] == '|':
                self._rd_open_pipe(self.chop(file))
            else:
                try:
                    self._fd = open(file, 'r')
                except IOError:
                    eprint('failed to open pipe to %s' % (file))

    def __del__(self):
        if self._pipe != None:
            self._pipe.terminate()
            self._pipe.communicate()
            del self._pipe
        elif self._fd != None:
            self._fd.close()

    def __exit__(self, type, val, traceback):
        if self._pipe != None:
            self._pipe.terminate()
            self._pipe.communicate()
            del self._pipe
        elif self._fd != None:
            self._fd.close()

    def _parse_command(self, cmd):
        m = re.search(r'(\||<|>|`|;)', cmd)
        if m:
            return "sh -c '" + cmd + "'"
        return cmd

    def _rd_open_pipe(self, cmd):
        try:
            cmd = self._parse_command(cmd)
            self._pipe = subprocess.Popen(shlex.split(cmd),
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
            self._fd = self._pipe.stdout
        except IOError:
            eprint('failed to open pipe from %s' % (cmd))

    #
    # returns file descriptor
    #
    def fd(self):
        return self._fd

    #
    # main loop
    #
    def runLoop(self, func, doStrip = True, *argv):
        for line in self._fd:
            if self._pipe != None:
                line = line.decode()
            if doStrip is True:
                line = line.strip()

            #
            # do something
            #   typical thing to do: col = line.split()
            # break the loop if the return value is 'False' and return 'False'
            #
            if func(self, line, *argv) ==  False:
                return False
        return True

    #
    # chop off the last character
    #
    def chop(self, line):
        return line[:len(line) - 1]


import tempfile
import unittest
import stat

class Testgetline(unittest.TestCase):
    def runTest(self):
        file = '/etc/passwd'
        eprint('')
        rc = self.pipeTest(file)
        rc2 = self.fileTest(file)
        if rc == True:
            rc = rc2
        rc2 = self.stdinTest(file)
        if rc == True:
            rc = rc2
        return rc

    def stdinTest(self, file):
        eprint('stdinTest...')
        flag = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | \
               stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
        fp = []
        for s in [ StdinTestPy, StdinTestSh ]:
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(s.encode())
            f.close()
            os.chmod(f.name, flag)
            fp.append(f)

        eprint('  python: %s' % fp[0].name)
        eprint('  shell: %s' % fp[1].name)
        rc = subprocess.call([fp[1].name, fp[0].name])
        for f in fp:
            os.unlink(f.name)

        if rc == 0:
            eprint('Passed')
            rc = True
        else:
            eprint('Failed')
            rc = False

        return rc


    def pipeTest(self, file):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        rc = self.execTest('cat %s |' % file, file, tmp)
        if rc == True:
            result = 'Passed'
        else:
            result = 'Failed'

        eprint('pipeTest: %s' % result)
        return rc


    def fileTest(self, file):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        rc = self.execTest(file, file, tmp)
        if rc == True:
            result = 'Passed'
        else:
            result = 'Failed'

        eprint('fileTest: %s' % result)
        return rc


    def execTest(self, inStr, file, tmp):
        obj = getline(inStr)
        obj.runLoop(self.processLine, False, tmp)
        del obj
        tmp.close()
        cmd = r'diff %s %s > /dev/null' % (file, tmp.name)
        rc = subprocess.call(cmd, shell=True)
        if rc == 0:
            os.unlink(tmp.name)
            return True
        else:
            eprint('ERROR. Temporary file name: %s' % (tmp.name))
            return False

    #
    # argv[0]: file descriptor of the tmp file
    #
    def processLine(self, p, line, *argv):
        argv[0].write((str(line)).encode())
        return True


###
### test scripts for stdinTest()
###

StdinTestPy = '''#!/usr/bin/env python3

import getline3
import sys
import tempfile

getline = getline3.getline

def processLine(p, line, *argv):
    sys.stdout.write(line)
    return True

def main():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    obj = getline('-') # read from stdin
    obj.runLoop(processLine, False, 0)

if __name__ == '__main__':
    main()
'''

StdinTestSh = '''#!/bin/sh
#
# Usage: ./test.sh ./test.py
#

if [ $# -lt 1 ]; then
  echo "ERROR: need an argument" 1>&2
  exit 1
fi
echo "  output: /tmp/$$.txt" 1>&2

cat /etc/passwd | $1 > /tmp/$$.txt
diff /etc/passwd /tmp/$$.txt
rc=$?
rm -f /tmp/$$.txt
exit $rc
'''
