#!/usr/bin/env python
# coding: UTF-8

from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
import sys,re,os,glob

debug=1     # 0:off, 1:print debug message
init=1      # 0:off, 1:put init code
files = []
lfcode = "\r\n"     # line feed code dos="\r\n", unix="\n"

# specifying a file name
if len(sys.argv) > 1:
    for filename in sys.argv[1:]:
        if re.match(r'..*\.jack', filename):
            files.append(filename)
        else:
            print "Error : not found a jack file", cmdtype
            sys.exit()
# specifying a dir name
else:
    files = glob.glob('*.jack')

# remove the asm file
for filename in files:
    tmp = re.sub(r'\.jack', '.xml', filename)
    if os.path.exists(tmp):
        os.remove(tmp)
        if debug: print "rm : ", tmp
    else:
        if debug: print "not exist : ", tmp
    tmp = re.sub(r'\.jack', 'T.xml', filename)
    if os.path.exists(tmp):
        os.remove(tmp)
        if debug: print "rm : ", tmp
    else:
        if debug: print "not exist : ", tmp


while len(files):
    filename = files.pop(0)
    if debug: print "load source filename : ", filename
    J = JackTokenizer(filename)
    J.write_all(re.sub(r'\.jack', 'T.xml', filename))

    J = JackTokenizer(filename)
    C = CompilationEngine(re.sub(r'\.jack', '.xml', filename), J)
    C.compileClass()

