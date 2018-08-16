#!/usr/bin/env python
# coding: UTF-8

from parser import parser
from codewriter import codewriter
import sys,re,os,glob

debug=1     # 0:off, 1:print debug message
files = []


filename = sys.argv[1]
# specifying a file name
if re.match(r'..*\.vm', filename):
    mode='file'
    tmp = re.sub(r'\.vm', '.asm', filename)
    files.append(filename)
# specifying a dir name
else:
    mode = 'dir'
    tmp = filename + '.asm'
    files = glob.glob('*.vm')

# remove the asm file
if os.path.exists(tmp):
    os.remove(tmp)
    if debug: print "rm : ", tmp
else:
    if debug: print "not exist : ", tmp

# open dest file
c = codewriter(tmp)


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

c.close

