#!/usr/bin/env python

import re

class parser():

    def __init__(self, filename):
        self.asmlist = []
        self.command = ''
        for line in open(filename, "r"):
            line = re.sub(r"\r\n", r"\n", line)     # cr+lf to lf
            line = re.sub(r"//.*", "", line)        # delete commnet
            line = re.sub(r"[ 	]", "", line, 0)    # delete whitespace
            if not re.match(r"^\n", line):
                #print "registered : ", line,
                self.asmlist.append(line[:-1])

    def fileopen(self, filename):
        self.__init__(filename)

    def hasMoreCommands(self):
        #print "hasMoreCommands : ", len(self.asmlist) > 0
        return len(self.asmlist) > 0

    def advance(self):
        self.command = self.asmlist.pop(0)
        #print "advance : ", self.command

    def commandType(self):
        if re.match(r"^[ 	]*@", self.command):
            tmp = "A_COMMAND"
        elif re.match(r"^[ 	]*\(", self.command):
            tmp = "L_COMMAND"
        else:
            tmp = "C_COMMAND"
        #print "commandType : ", tmp
        return tmp

    def symbol(self):
        if re.match(r"^[ 	]*@", self.command):
            tmp = self.command[1:]
        elif re.match(r"^[ 	]*\(", self.command):
            tmp = self.command[1:-1]
        #print "symbol : ", tmp
        return tmp

    def dest(self):
        tmp = re.sub(r"=..*", "", self.command)
        tmp = re.sub(r"..*;J.*", "", tmp)
        #print "dest : ", tmp
        return tmp

    def comp(self):
        tmp = re.sub(r".*=", "", self.command)
        tmp = re.sub(r";..*", "", tmp)
        #print "comp : ", tmp
        return tmp

    def jump(self):
        tmp = re.sub(r"..*;", "", self.command)
        #print "jump : ", tmp
        return tmp

    def test(self):
        while self.hasMoreCommands():
            self.advance()
            if self.commandType() in ("A_COMMAND", "L_COMMAND"):
                self.symbol()
            else:
                self.dest()
                self.comp()
                self.jump()

# test
#p = parser("hoge.asm")
#p.test()


