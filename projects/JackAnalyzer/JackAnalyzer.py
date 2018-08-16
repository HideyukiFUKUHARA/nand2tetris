#!/usr/bin/env python
# coding: UTF-8

from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
import sys,re,os,glob

debug=1     # 0:off, 1:print debug message
init=1      # 0:off, 1:put init code
files = []

filename = sys.argv[1]
# specifying a file name
if re.match(r'..*\.jack', filename):
    files.append(filename)
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



# open dest file
c = codewriter(tmp)
if init: c.writeInit()


while len(files):
    filename = files.pop(0)
    if debug: print "load source filename : ", filename
    c.setFileName(filename)
    p = parser(filename)
    while p.hasMoreCommands():
        p.advance()
        cmdtype = p.commandType()
        if   cmdtype in ('C_PUSH', 'C_POP'):
            c.writePushPop(cmdtype, p.arg1(), p.arg2())
        elif cmdtype == 'C_ARITHMETIC':
            c.writeArithmetic(p.arg1())
        elif cmdtype == 'C_LABEL':
            c.writeLabel(p.arg1())
        elif cmdtype == 'C_GOTO':
            c.writeGoto(p.arg1())
        elif cmdtype == 'C_IF':
            c.writeIf(p.arg1())
        elif cmdtype == 'C_FUNCTION':
            c.writeFunction(p.arg1(), p.arg2())
        elif cmdtype == 'C_RETURN':
            c.writeReturn()
        elif cmdtype == 'C_CALL':
            c.writeCall(p.arg1(), p.arg2())
        else:
            print "Error : undefined cmdtype", cmdtype
            sys.exit()

c.close

