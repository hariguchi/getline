r''' getline - get each line from a file or stdin; each line is passed to the specified function

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


Usage:
  import getline

  Example 1:
    #
    # p:      instance of class getline
    # line:   the line to be processed
    # argv[]: parameters from the caller of p.runLoop()
    #
    def processLine(p, line, *argv):
        r = re.compile(r'^[0-9]*$')
        line = p.chop(line)
        m = r.search(line)
        if m != None:
            print line

    #
    # processLine().argv[0] == 1
    # processLine().argv[1] == 2
    #
    obj = getline.getline('file')         # read from file 'file'
    obj.runLoop(processLine, False, 1, 2) # do not strip lines

  Example 2:
    #
    # p:      instance of class getline
    # line:   the line to be processed
    # argv[]: parameters from the caller of p.runLoop()
    #
    def processLine(p, line, *argv):
        line = p.chop(line)
        print line

    #
    # processLine().argv[0] == 1
    # processLine().argv[1] == 2
    #
    obj = getline.getline('-')           # read from stdin
    obj.runLoop(processLine, True, 1, 2) # strip lines

'''


import os
import sys

class getline:
    def __init__(self, file):
        if file == '-':
            self.fd = sys.stdin
        else:
            try:
                file = file.strip()
                self.fd = open(file, 'r')
            except IOError:
                print >> sys.stderr, 'failed to open pipe to %s' % (file)

    def __del__(self):
        self.fd.close()

    def __exit__(self, type, val, traceback):
        self.close()

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
            #
            func(self, line, *argv)

    #
    # chop off the last character
    #
    def chop(self, line):
        return line[:len(line) - 1]

