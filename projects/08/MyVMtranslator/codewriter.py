#!/usr/bin/env python
# coding: UTF-8

import re, sys

class codewriter():

    debug = 1           # 0:off, 1:print debug message
    lfcode = "\r\n"     #line feed code dos="\r\n", unix="\n"
    labelnum = 0
    funcname = ''
    uniqID = 0

    def __init__(self, filename):
        self.asmfile = open(filename, "a")
        self.nextpc = 0     # for debug

    def setFileName(self, filename):
        # get vmname
        self.vmname = re.sub(r'\.vm', '', filename)

    def writeInit(self):
        if self.debug: print "writeInit : "
        list = []
        # sp = 256
        list.append('    @256')         # 0 :
        list.append('    D=A')          # 1 : RAM[SP-1]:y
        list.append('    @SP')          # 2 :
        list.append('    M=D')          # 3 :
        self.nextpc += 4
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc
        # call Sys.init
        self.writeCall('Sys.init', 0)

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
            self.nextpc += 5
        # --------------------------------------------------------
        elif command in ('neg', 'not'):
            list.append('    @SP')          # 0 : RAM[SP]
            list.append('    A=M-1')        # 1 : RAM[SP-1]:y
            if   command == 'neg':
                list.append('    M=-M')         # 2 : -y
            elif command == 'not':
                list.append('    M=!M')         # 2 : !y
            self.nextpc += 3
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
            list.append('    D=-1')         # 10 : true
            list.append('(JJOIN_{:03d})'.format(self.labelnum)) # 11 :
            list.append('    @SP')          # 11 : RAM[SP]
            list.append('    A=M-1')        # 12 : RAM[SP-1]
            list.append('    M=D')          # 13 :
            self.labelnum += 1
            self.nextpc += 13
        # --------------------------------------------------------
        else:
            print "Error : undefined command in vmfile", command
            sys.exit()
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

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
                self.nextpc += 9
            elif segment in ('pointer', 'temp'):
                if   segment == 'pointer':
                    list.append('    @{:d}'.format(3+int(index)))   # 0 :   THIS + index
                elif segment == 'temp':
                    list.append('    @{:d}'.format(5+int(index)))   # 0 :   TMP + index
                list.append('    D=M')      # 1 :   get data
                list.append('    @SP')      # 2 :   RAM[0]
                list.append('    A=M')      # 3 :   RAM[SP]
                list.append('    M=D')      # 4 :   RAM[SP] = data
                list.append('    @SP')      # 5 :   RAM[0]
                list.append('    M=M+1')    # 6 :   SP+1
                self.nextpc += 7
            elif segment == 'constant':
                list.append('    @{:d}'.format(int(index))) # 0 :
                list.append('    D=A')      # 1 :   set data
                list.append('    @SP')      # 2 :   RAM[0]
                list.append('    A=M')      # 3 :   RAM[SP]
                list.append('    M=D')      # 4 :   RAM[SP] = data
                list.append('    @SP')      # 5 :   RAM[0]
                list.append('    M=M+1')    # 6 :   SP+1
                self.nextpc += 7
            elif segment == 'static':
                list.append('    @{:s}.{:d}'.format(self.vmname, int(index))) #  0 :
                list.append('    D=M')      # 1 :   get offset
                list.append('    @SP')      # 2 :
                list.append('    A=M')      # 3 :   RAM[SP]
                list.append('    M=D')      # 4 :   RAM[SP] = data
                list.append('    @SP')      # 5 :   RAM[0]
                list.append('    M=M+1')    # 6 :   SP+1
                self.nextpc += 7
            else:
                print "Error : undefined segment"
                sys.exit()
        # --------------------------------------------------------
        elif command == 'C_POP':
            if   segment in ('local', 'argument', 'this', 'that'):
                list.append('    @{:d}'.format(int(index))) #   :
                list.append('    D=A')      #   :   get offset
                if   segment == 'local':    #   :   get base
                    list.append('    @LCL')
                elif segment == 'argument':
                    list.append('    @ARG')
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
                self.nextpc += 12
            elif segment in ('pointer','temp'):
                list.append('    @SP')      # 0 :   RAM[0]
                list.append('    AM=M-1')   # 1 :   SP-1, RAM[SP-1]
                list.append('    D=M')      # 2 :   get RAM[SP-1]
                if   segment == 'pointer':
                    list.append('    @{:d}'.format(3+int(index))) # 3 :
                elif segment == 'temp':
                    list.append('    @{:d}'.format(5+int(index))) # 3 :
                list.append('    M=D')      # 4 :
                self.nextpc += 5
            elif segment == 'constant':
                list.append('    @SP')      # RAM[0]
                list.append('    AM=M-1')   # SP-1
                list.append('    D=M')      # get RAM[SP-1]
                self.nextpc += 3
            elif segment == 'static':
                list.append('    @SP')      # 0 :   RAM[0]
                list.append('    AM=M-1')   # 1 :   SP-1, RAM[SP-1]
                list.append('    D=M')      # 2 :   get RAM[SP-1]
                list.append('    @{:s}.{:d}'.format(self.vmname, int(index))) #  3 :
                list.append('    M=D')      # 4 :   RAM[Xxx.j] = data
                self.nextpc += 5
            else:
                print "Error : undefined segment"
                sys.exit()
        # --------------------------------------------------------
        else:
            print "Error : undefined command", command
            sys.exit()
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def writeLabel(self, label):
        if self.debug: print "writeLabel : ", label
        list = []
        list.append('({:s})'.format(label)) # 0 :
        self.nextpc += 0
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def writeGoto(self, label):
        if self.debug: print "writeGoto : ", label
        list = []
        list.append('    @{:s}'.format(label))  # 0 :
        list.append('    0;JMP')    # 1 :
        self.nextpc += 2
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def writeIf(self, label):
        if self.debug: print "writeIf : ", label
        list = []
        list.append('    @SP')      # 0 :   RAM[SP]
        list.append('    AM=M-1')   # 1 :   SP-1, RAM[SP-1]
        list.append('    D=M')      # 2 :   get data
        list.append('    @{:s}'.format(label))  # 3 :
        list.append('    D;JNE')    # 4 :
        self.nextpc += 5
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def writeCall(self, functionName, numArgs):
        if self.debug: print "writeCall : ", functionName, numArgs
        list = []
        list.append('    @{:s}$return{:d}'.format(functionName, self.uniqID))     # 0 :   A=return_address
        list.append('    D=A')      # 0 :   D=return_address
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    M=D')      # 0 :   RAM[SP]=return_address
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    M=M+1')    # 0 :   SP+1

        list.append('    @LCL')     # 0 :   RAM[LCL]
        list.append('    D=M')      # 0 :   D=RAM[LCL]
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    A=M')      # 0 :   RAM[SP]
        list.append('    M=D')      # 0 :   RAM[SP]=RAM[LCL]
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    M=M+1')    # 0 :   SP+1

        list.append('    @ARG')     # 0 :   RAM[ARG]
        list.append('    D=M')      # 0 :   D=RAM[ARG]
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    A=M')      # 0 :   RAM[SP]
        list.append('    M=D')      # 0 :   RAM[SP]=RAM[ARG]
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    M=M+1')    # 0 :   SP+1

        list.append('    @THIS')    # 0 :   RAM[THIS]
        list.append('    D=M')      # 0 :   D=RAM[THIS]
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    A=M')      # 0 :   RAM[SP]
        list.append('    M=D')      # 0 :   RAM[SP]=RAM[THIS]
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    M=M+1')    # 0 :   SP+1

        list.append('    @THAT')    # 0 :   RAM[THAT]
        list.append('    D=M')      # 0 :   D=RAM[THAT]
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    A=M')      # 0 :   RAM[SP]
        list.append('    M=D')      # 0 :   RAM[SP]=RAM[THAT]
        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    M=M+1')    # 0 :   SP+1

        list.append('    @SP')      # 0 :   RAM[0]
        list.append('    D=M')      # 0 :   D=SP
        list.append('    @LCL')     # 0 :   RAM[LCL]
        list.append('    M=D')      # 0 :   RAM[LCL]=SP
        list.append('    @{:d}'.format(int(numArgs)))    # A=numArgs
        list.append('    D=D-A')    # 0 :   D=SP-numArgs
        list.append('    @5')       # 0 :   A=5
        list.append('    D=D-A')    # 0 :   D=SP-numArgs-5
        list.append('    @ARG')     # 0 :   RAM[ARG]
        list.append('    M=D')      # 0 :   RAM[ARG]=SP-numArgs-5

        list.append('    @{:s}'.format(functionName))
        list.append('    0;JMP')    # 0 :   

        list.append('({:s}$return{:d})'.format(functionName, self.uniqID))     # 0 :   A=return_address
        self.uniqID +=1

        self.nextpc += 5
        self.funcname = ''
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def writeFunction(self, functionName, numLocals):
        if self.debug: print "writeFunction : ", functionName, numLocals
        list = []
        list.append('({:s})'.format(functionName))  # 0 :   Function Label
        for i in range(int(numLocals)):
            list.append('    @SP')      # 0 :   RAM[0]
            list.append('    A=M')      # 1 :   RAM[SP]
            list.append('    M=0')      # 2 :   RAM[SP] = 0
            list.append('    @SP')      # 3 :   RAM[0]
            list.append('    M=M+1')    # 4 :   SP+1
        self.nextpc += (5 * int(numLocals))
        self.funcname = functionName + '$'
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def writeReturn(self):
        if self.debug: print "writeReturn : "
        list = []
        list.append('    @LCL')     # 0 :   A=LCL
        list.append('    D=M')      # 1 :   D=RAM[LCL]
        list.append('    @R13')     # 2 :   A=13
        list.append('    M=D')      # 3 :   RAM[13]=RAM[LCL]
        # get return value
        list.append('    @SP')      # 4 :   A=SP
        list.append('    A=M-1')    # 5 :   A=RAM[SP]-1
        list.append('    D=M')      # 6 :   D=return_value
        list.append('    @ARG')     # 7 :   A=ARG
        list.append('    A=M')      # 8 :   A=RAM[ARG]
        list.append('    M=D')      # 9 :   RAM[ARG]=return_value
        # set SP
        list.append('    @ARG')     # 10 :   A=ARG
        list.append('    D=M+1')    # 11 :   D=RAM[ARG]+1
        list.append('    @SP')      # 12 :   A=SP
        list.append('    M=D')      # 13 :   RAM[SP]=RAMARG]+1
        # set THAT
        list.append('    @R13')     # 14 :   A=13
        list.append('    D=M')      # 15 :   D=RAM[13]
        list.append('    @1')       # 16 :   A=1
        list.append('    A=D-A')    # 17 :   A=RAM[13]-1
        list.append('    D=M')      # 18 :   D=RAM[RAM[13]-1]
        list.append('    @THAT')    # 19 :   A=THAT
        list.append('    M=D')      # 20 :   RAM[THAT]=D
        # set THIS
        list.append('    @R13')     # 21 :   A=13
        list.append('    D=M')      # 22 :   D=RAM[13]
        list.append('    @2')       # 23 :   A=2
        list.append('    A=D-A')    # 24 :   A=RAM[13]-2
        list.append('    D=M')      # 25 :   D=RAM[RAM[13]-2]
        list.append('    @THIS')    # 26 :   A=THIS
        list.append('    M=D')      # 27 :   RAM[THIS]=D
        # set ARG
        list.append('    @R13')     # 28 :   A=13
        list.append('    D=M')      # 29 :   D=RAM[13]
        list.append('    @3')       # 30 :   A=3
        list.append('    A=D-A')    # 31 :   A=RAM[13]-3
        list.append('    D=M')      # 32 :   D=RAM[RAM[13]-3]
        list.append('    @ARG')     # 33 :   A=ARG
        list.append('    M=D')      # 34 :   RAM[ARG]=D
        # set LCL
        list.append('    @R13')     # 35 :   A=13
        list.append('    D=M')      # 36 :   D=RAM[13]
        list.append('    @4')       # 37 :   A=3
        list.append('    A=D-A')    # 38 :   A=RAM[13]-4
        list.append('    D=M')      # 39 :   D=RAM[RAM[13]-4]
        list.append('    @LCL')     # 40 :   A=LCL
        list.append('    M=D')      # 41 :   RAM[LCL]=D
        # goto RET
        list.append('    @R13')     # 42 :   A=13
        list.append('    D=M')      # 43 :   D=RAM[13]
        list.append('    @5')       # 44 :   A=5
        list.append('    A=D-A')    # 45 :   A=RAM[13]-5
        list.append('    0;JMP')    # 46 :
        self.nextpc += 47
        self.funcname = ''
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc


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


