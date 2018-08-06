#!/usr/bin/env python
# coding: UTF-8

import re

class parser():

    debug=1     # 0:off, 1:print debug message

    def __init__(self, filename):
        self.vmlist = []
        self.command = ''
        for line in open(filename, "r"):
            line = re.sub(r"\r\n", r"\n", line)     # cr+lf to lf
            line = re.sub(r"//.*", "", line)        # delete commnet
            line = re.sub(r"^[ 	].*", "", line, 0)  # delete ahead whitespace
            if not re.match(r"^\n", line):
                if self.debug: print "registered : ", line,
                self.vmlist.append(line[:-1])

    def fileopen(self, filename):
        self.__init__(filename)

    def hasMoreCommands(self):
        if self.debug: print "hasMoreCommands : ", len(self.vmlist) > 0
        return len(self.vmlist) > 0

    def advance(self):
        self.command = self.vmlist.pop(0)
        if self.debug: print "advance : ", self.command

    def commandType(self):
        cmd = self.command.split()[0]
        if   cmd in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'):
                                 tmp = "C_ARITHMETIC"
        elif cmd == 'push'     : tmp = "C_PUSH"
        elif cmd == 'pop'      : tmp = "C_POP"
        elif cmd == 'label'    : tmp = "C_LABEL"
        elif cmd == 'goto'     : tmp = "C_GOTO"
        elif cmd == 'if-goto'  : tmp = "C_IF"
        elif cmd == 'function' : tmp = "C_FUNCTION"
        elif cmd == 'return'   : tmp = "C_RETURN"
        elif cmd == 'call'     : tmp = "C_CALL"
        else                   : print "Error : undefined commnad"
        if self.debug: print "commandType : ", tmp
        return tmp

    def arg1(self):
        cmd = self.command.split()[0]
        if   cmd in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'):
                                 tmp = cmd
        elif cmd == 'push'     : tmp = self.command.split()[1]
        elif cmd == 'pop'      : tmp = self.command.split()[1]
        elif cmd == 'label'    : tmp = self.command.split()[1]
        elif cmd == 'goto'     : tmp = self.command.split()[1]
        elif cmd == 'if-goto'  : tmp = self.command.split()[1]
        elif cmd == 'function' : tmp = self.command.split()[1]
        elif cmd == 'return'   : tmp = ""
        elif cmd == 'call'     : tmp = self.command.split()[1]
        else                   : print "Error : undefined commnad"
        if self.debug: print "arg1 : ", tmp
        return tmp

    def arg2(self):
        cmd = self.command.split()[0]
        if   cmd in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'):
                                 tmp = ""
        elif cmd == 'push'     : tmp = self.command.split()[2]
        elif cmd == 'pop'      : tmp = self.command.split()[2]
        elif cmd == 'label'    : tmp = ""
        elif cmd == 'goto'     : tmp = ""
        elif cmd == 'if-goto'  : tmp = ""
        elif cmd == 'function' : tmp = self.command.split()[2]
        elif cmd == 'return'   : tmp = ""
        elif cmd == 'call'     : tmp = self.command.split()[2]
        else                   : print "Error : undefined commnad"
        if self.debug: print "arg2 : ", tmp
        return tmp

    def test(self):
        while self.hasMoreCommands():
            self.advance()
            self.commandType()
            self.arg1()
            self.arg2()


# test
#p = parser("hoge.vm")
#p.test()


