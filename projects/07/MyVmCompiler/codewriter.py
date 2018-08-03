#!/usr/bin/env python
# coding: UTF-8

import re

class codewriter():

    debug=1         # 0:off, 1:print debug message
    lfcode="\r\n"   #line feed code dos="\r\n", unix="\n"
    labelnum=0

    def __init__(self, filename):
        self.asmfile = open(filename, "w")
        # initialize SP=256
        list = []
        list.append('    @256')
        list.append('    D=A')
        list.append('    @SP')
        list.append('    M=D')
        # get vmname
        if re.match(r'\.vm', filename):
            self.vmname = re.sub(r'\.vm', '', filename)
        else: # not has extension
            self.vmname = filename
        # output
        for i in list:
            if self.debug: print i
            self.asmfile.write(i+self.lfcode)

    def setFileName(self, filename):
        self.__init__(filename)

    def writeArithmetic(self, command):
        if self.debug: print "writeArithmetic : ", command
        list = []
        # --------------------------------------------------------
        if   command in ('add', 'sub', 'and', 'or'):
            list.append('    @SP')          # 0 : RAM[SP]
            list.append('    AM=M-1')       # 1 : RAM[SP-1]:y
            list.append('    D=M')          # 2 :
            list.append('    A=A-1')        # 3 : RAM[SP-2]:x
            if   command == 'add':
                list.append('    M=M+D')    # 4 : x + y
            elif command == 'sub':
                list.append('    M=M-D')    # 4 : x - y
            elif command == 'and':
                list.append('    M=M&D')    # 4 : x & y
            elif command == 'or':
                list.append('    M=M|D')    # 4 : x | y
        # --------------------------------------------------------
        elif command in ('neg', 'not'):
            list.append('    @SP')          # 0 : RAM[SP]
            list.append('    A=M-1')        # 1 : RAM[SP-1]:y
            if   command == 'neg':
                list.append('    M=-M')         # 2 : -y
            elif command == 'not':
                list.append('    M=!M')         # 2 : !y
        # --------------------------------------------------------
        elif command in ('eq', 'gt', 'lt'):
            list.append('    @SP')          # 0 : RAM[SP]
            list.append('    AM=M-1')       # 1 : RAM[SP-1]:x
            list.append('    D=M')          # 2 : 
            list.append('    A=A-1')        # 3 : RAM[SP-2]:y
            list.append('    D=M-D')        # 4 : x-y
            list.append('    @JTRUE_{:03d}'.format(self.labelnum)) # 5 : 
            if   command == 'eq':
                list.append('    D;JEQ')    # 6 : x eq y
            elif command == 'gt':
                list.append('    D;JGT')    # 6 : x gt y
            elif command == 'lt':
                list.append('    D;JLT')    # 6 : x lt y
            list.append('    D=0')          # 7 : false
            list.append('    @JJOIN_{:03d}'.format(self.labelnum)) # 8 :
            list.append('    0;JMP')        # 9 : jump
            list.append('(JTRUE_{:03d})'.format(self.labelnum)) # 10 :
            list.append('    D=-1')         # 11 : true
            list.append('(JJOIN_{:03d})'.format(self.labelnum)) # 12 :
            list.append('    @SP')          # 13 : RAM[SP]
            list.append('    A=M-1')        # 14 : RAM[SP-1]
            list.append('    M=D')          # 15 :
            self.labelnum += 1
        # --------------------------------------------------------
        else:
            print "Error : undefined command in vmfile", command
        # output
        for i in list:
            if self.debug: print i
            self.asmfile.write(i+self.lfcode)

    def writePushPop(self, command, segment, index):
        if self.debug: print "writePushPop : ", command, segment, index
        list = []
        # --------------------------------------------------------
        if command == 'C_PUSH':
            if   segment in ('local', 'argument', 'this', 'that'):
                list.append('    @{:d}'.format(int(index))) # 0 :
                list.append('    D=A')      # 1 :   get offset
                if   segment == 'local':    # 2 :   get base:
                    list.append('    @LCL')
                elif segment == 'argument':
                    list.append('    @ARG')
                elif segment == 'this':
                    list.append('    @THIS')
                elif segment == 'that':
                    list.append('    @THAT')
                list.append('    A=M+D')    # 3 :   base+offset
                list.append('    D=M')      # 4 :   get data
                list.append('    @SP')      # 5 :
                list.append('    A=M')      # 6 :   RAM[SP]
                list.append('    M=D')      # 7 :   RAM[SP] = data
                list.append('    @SP')      # 5 :   RAM[0]
                list.append('    M=M+1')    # 8 :   SP+1
            elif segment in ('pointer', 'tmp'):
                if   segment == 'pointer':
                    list.append('    @{:d}'.format(3+int(index)))   # 0 :   THIS + index
                elif segment == 'tmp':
                    list.append('    @{:d}'.format(5+int(index)))   # 0 :   TMP + index
                list.append('    D=M')      # 1 :   get data
                list.append('    @SP')      # 2 :   RAM[0]
                list.append('    A=M')      # 3 :   RAM[SP]
                list.append('    M=D')      # 4 :   RAM[SP] = data
                list.append('    @SP')      # 5 :   RAM[0]
                list.append('    M=M+1')    # 6 :   SP+1
            elif segment == 'constant':
                list.append('    @{:d}'.format(int(index))) # 0 :
                list.append('    D=A')      # 1 :   set data
                list.append('    @SP')      # 2 :   RAM[0]
                list.append('    A=M')      # 3 :   RAM[SP]
                list.append('    M=D')      # 4 :   RAM[SP] = data
                list.append('    @SP')      # 5 :   RAM[0]
                list.append('    M=M+1')    # 6 :   SP+1
            elif segment == 'static':
                list.append('    @{:s}.{:d}'.format(self.vmname, index)) #  0 :
                list.append('    D=M')      # 1 :   get offset
                list.append('    @SP')      # 2 :
                list.append('    A=M')      # 3 :   RAM[SP]
                list.append('    M=D')      # 4 :   RAM[SP] = data
                list.append('    @SP')      # 2 :   RAM[0]
                list.append('    M=M+1')    # 5 :   SP+1
            else                   : print "Error : undefined segment"
        # --------------------------------------------------------
        elif command == 'C_POP':
            if   segment in ('local', 'argument', 'this', 'that'):
                list.append('    @{:d}'.format(int(index))) #   :
                list.append('    D=M')      #   :   get offset
                if   segment == 'local':    #   :   get base
                    list.append('    @LCL')
                elif segment == 'argument':
                    list.append('    @THAT')
                elif segment == 'this':
                    list.append('    @THIS')
                elif segment == 'that':
                    list.append('    @THAT')
                list.append('    D=D+M')    #   :   base+offset
                list.append('    @R15')     #   :   RAM[15]
                list.append('    M=D')      #   :   RAM[15] = base+offset
                list.append('    @SP')      #   :   RAM[0]
                list.append('    AM=M-1')   #   :   SP-1, RAM[SP-1]
                list.append('    D=M')      #   :   get RAM[SP-1]
                list.append('    @R15')     #   :   RAM[15]
                list.append('    A=M')      #   :   RAM[base+offset]
                list.append('    M=D')      #   :   RAM[base+offset] = RAM[SP-1]
            elif segment in ('pointer','tmp'):
                list.append('    @SP')      # 0 :   RAM[0]
                list.append('    AM=M-1')   # 1 :   SP-1, RAM[SP-1]
                list.append('    D=M')      # 2 :   get RAM[SP-1]
                if   segment == 'pointer':
                    list.append('    @{:d}'.format(3+int(index))) # 3 :
                elif segment == 'tmp':
                    list.append('    @{:d}'.format(5+int(index))) # 3 :
                list.append('    M=D')      # 4 :
            elif segment == 'constant':
                list.append('    @SP')      # RAM[0]
                list.append('    AM=M-1')   # SP-1
                list.append('    D=M')      # get RAM[SP-1]
            elif segment == 'static':
                list.append('    @SP')      # 0 :   RAM[0]
                list.append('    AM=M-1')   # 1 :   SP-1, RAM[SP-1]
                list.append('    D=M')      # 2 :   get RAM[SP-1]
                list.append('    @{:s}.{:d}'.format(self.vmname, index)) #  0 :
                list.append('    A=M')      # 1 :   get Xxx.j
                list.append('    M=D')      # 4 :   RAM[Xxx.j] = data
            else                   : print "Error : undefined segment"
        # --------------------------------------------------------
        else:
            print "Error : undefined command", command
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


