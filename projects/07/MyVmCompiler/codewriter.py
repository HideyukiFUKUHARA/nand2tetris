#!/usr/bin/env python
# coding: UTF-8

import re

class codewriter():

    debug=1         # 0:off, 1:print debug message
    lfcode="\r\n"   #line feed code dos="\r\n", unix="\n"

    def __init__(self, filename):
        self.asmfile = open(filename, "w")
        # initialize SP=256
        list = []
        list.append('    @256')
        list.append('    D=A')
        list.append('    @SP')
        list.append('    M=D')
        # output
        for i in list:
            if self.debug: print i
            self.asmfile.write(i+self.lfcode)

    def setFileName(self, filename):
        self.__init__(filename)

    def writeArithmetic(self, command):
        if self.debug: print "writeArithmetic : ", command
        list = []
        if command == 'add':
            list.append('    @SP')
            list.append('    M=M-1')
            list.append('    A=M')
            list.append('    D=M')
            list.append('    A=A-1')
            list.append('    M=D+M')
        # output
        for i in list:
            if self.debug: print i
            self.asmfile.write(i+self.lfcode)

    def writePushPop(self, command, segment, index):
        if self.debug: print "writePushPop : ", command, segment, index
        list = []
        if command == 'C_PUSH':
            if   segment == 'argument': pass
            elif segment == 'local': pass
            elif segment == 'static': pass
            elif segment == 'constant':
                list.append('    @{:d}'.format(int(index)))
                list.append('    D=A')
                list.append('    @SP')
                list.append('    A=M')
                list.append('    M=D')
                list.append('    @SP')
                list.append('    M=M+1')
            elif segment == 'this': pass
            elif segment == 'that': pass
            elif segment == 'pointer': pass
            elif segment == 'tmp': pass
            else                   : print "Error : undefined segment"
        # output
        for i in list:
            if self.debug: print i
            self.asmfile.write(i+self.lfcode)

    def close(self):
        self.asmfile.close()

    def test(self):
        self.writePushPop('C_PUSH', 'constant', 1234)
        self.writePushPop('C_PUSH', 'constant', 4321)
        self.writeArithmetic('add')
        self.close()

# test
#c = codewrite("hoge.asm")
#c.test()


