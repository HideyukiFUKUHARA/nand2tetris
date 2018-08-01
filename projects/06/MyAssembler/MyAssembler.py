#!/usr/bin/env python
# coding: UTF-8

from parser import parser
from code import code
from symtbl import symtbl
import sys, re


files = sys.argv[1:]
while len(files):
    filename = files.pop(0)
    p = parser(filename)
    c = code()
    s = symtbl()
    usrAddress = 16
    instAddress = 0
    dataAddress = 0
    # create symbol-table
    while p.hasMoreCommands():
        p.advance()
        if p.commandType() == 'L_COMMAND':
            if s.contains(p.symbol()):
                print "Error : contained label"
            else:
                s.addEntry(p.symbol(), instAddress)
                #print p.symbol(), instAddress
        elif p.commandType() == 'A_COMMAND':
            if re.match(r'[0-9].*', p.symbol()):
                pass
            elif s.contains(p.symbol()):
                pass
            else:
                s.addEntry(p.symbol(), usrAddress)
                #print p.symbol(), usrAddress
                usrAddress += 1
            instAddress += 1
        else:
            instAddress += 1
    # create romdata
    p.fileopen(filename)
    romfile = open(re.sub(r'asm', 'hack', filename), 'w')
    while p.hasMoreCommands():
        p.advance()
        if p.commandType() == 'C_COMMAND':
            str =  "111{:07b}{:03b}{:03b}".format(c.comp(p.comp()), c.dest(p.dest()), c.jump(p.jump()))
        elif p.commandType() == 'A_COMMAND':
            if re.match(r'[0-9].*', p.symbol()):
                adrs = int(p.symbol())
            elif s.contains(p.symbol()):
                adrs = s.getAddress(p.symbol())
            else:
                print "Error : not found label"
            str = "0{:015b}".format(adrs)
        else:   # L_COMMAND
            pass
        print str
        romfile.write(str + '\r\n')
    romfile.close



