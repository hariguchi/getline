r''' getline - Get each line from a stream

   Copyright (c) 2020 Yoichi Hariguchi
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
stream and pass it to the specified function. An input stream can be either
a regular file, stdin, or pipe.


Example:

import getline
import re

def main():
    #
    # 1. Instantiate getline object
    #
    f = getline.getline('/etc/passwd') # regular file
    s = getline.getline('-')           # stdin
    p = getline.getline('ls /etc |')   # pipe

    #
    # 2. Call the loop reading input stream
    #    1st param: function to be called each time a new line is read
    #               (let us call it processLine())
    #    2nd param: line is stripped if it is True
    #               line is *NOT* stripped if is False
    #    3rd param: all parameters from the 3rd are passed to processLine()
    #
    #    Return value:
    #     True: input stream reached EOF (end of file)
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
#  1st param:    pointer to the getline object
#  2nd param:    line to be processed
#  other params: passed from p.runLoop()
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


How to test the module:
  python -m unittest -v getline
'''

import os
import re
import shlex
import subprocess
import sys


class getline:
    def __init__(self, file):
        self.fd = None

        file = file.strip()
        if file == '-':
            self.fd = sys.stdin
        else:
            if file[len(file) - 1] == '|':
                self._rd_open_pipe(self.chop(file))
            else:
                try:
                    self.fd = open(file, 'r')
                except IOError:
                    print >> sys.stderr, 'failed to open pipe to %s' % (file)

    def __del__(self):
        if self.fd != None:
            self.fd.close()

    def __exit__(self, type, val, traceback):
        if self.fd != None:
            self.fd.close()

    def _parse_command(self, cmd):
        m = re.search(r'(\||<|>|`|;)', cmd)
        if m:
            return "sh -c '" + cmd + "'"
        return cmd

    def _rd_open_pipe(self, cmd):
        try:
            cmd = self._parse_command(cmd)
            self._proc = subprocess.Popen(shlex.split(cmd),
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
            self.fd = self._proc.stdout
        except IOError:
            print >> sys.stderr, 'failed to open pipe from %s' % (cmd)

    #
    # main loop
    #
    def runLoop(self, func, doStrip = True, *argv):
        #
        # Use readlines() for a small file since it reads entire file at once.
        # xreadlines() read one line at a time.
        #
        for line in self.fd.xreadlines():
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
        sys.stderr.write('\n')
        rc = self.pipeTest(file)
        rc2 = self.fileTest(file)
        if rc == True:
            rc = rc2
        rc2 = self.stdinTest(file)
        if rc == True:
            rc = rc2
        return rc

    def stdinTest(self, file):
        sys.stderr.write('stdinTest...\n')
        flag = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | \
               stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
        fp = []
        for s in [ StdinTestPy, StdinTestSh ]:
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(s)
            f.close()
            os.chmod(f.name, flag)
            fp.append(f)

        sys.stderr.write('  python: %s\n' % fp[0].name)
        sys.stderr.write('  shell: %s\n' % fp[1].name)
        rc = subprocess.call([fp[1].name, fp[0].name])
        for f in fp:
            os.unlink(f.name)

        if rc == 0:
            sys.stderr.write('Passed\n')
            rc = True
        else:
            sys.stderr.write('Failed\n')
            rc = False

        sys.stderr.flush()
        return rc


    def pipeTest(self, file):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        rc = self.execTest('cat %s |' % file, file, tmp)
        if rc == True:
            result = 'Passed'
        else:
            result = 'Failed'

        sys.stderr.write('pipeTest: %s\n' % result)
        sys.stderr.flush()
        return rc


    def fileTest(self, file):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        rc = self.execTest(file, file, tmp)
        if rc == True:
            result = 'Passed'
        else:
            result = 'Failed'

        sys.stderr.write('fileTest: %s\n' % result)
        sys.stderr.flush()
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
            print 'ERROR. Temporary file name: %s' % tmp.name
            return False

    #
    # argv[0]: file descriptor of the tmp file
    #
    def processLine(self, p, line, *argv):
        argv[0].write(line)
        return True


###
### test scripts for stdinTest()
###

StdinTestPy = '''#!/usr/bin/env python

import getline
import sys
import tempfile


def processLine(p, line, *argv):
    sys.stdout.write(line)
    return True

def main():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    obj = getline.getline('-') # read from stdin
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
