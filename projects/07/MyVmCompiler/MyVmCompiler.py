#!/usr/bin/env python
# coding: UTF-8

from parser import parser
from codewriter import codewriter
import sys,re

debug=1     # 0:off, 1:print debug message

files = sys.argv[1:]
while len(files):
    filename = files.pop(0)
    if debug: print "load filename : ", filename
    p = parser(filename)
    c = codewriter(re.sub(r'\.vm', '.asm', filename))
    while p.hasMoreCommands():
        p.advance()
        cmdtype = p.commandType()
        if   cmdtype == 'C_PUSH':
            c.writePushPop(cmdtype, p.arg1(), p.arg2())
        elif cmdtype == 'C_ARITHMETIC':
            c.writeArithmetic(p.arg1())
        print "hoge"

