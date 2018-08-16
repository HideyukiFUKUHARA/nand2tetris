#!/usr/bin/env python
# coding: UTF-8

import re, sys

class codewriter():

    debug = 1           # 0:off, 1:print debug message
    lfcode = "\r\n"     #line feed code dos="\r\n", unix="\n"
    jumpID = 0
    uniqID = 0
    funcname = ''

    def __init__(self, filename):
        self.asmfile = open(filename, "a")
        self.nextpc = 0     # for debug

    def setFileName(self, filename):
        # get vmname
        self.vmname = re.sub(r'\.vm', '', filename)

    def writeInit(self):
        if self.debug: print "writeInit : "
        list = []
        list.append('    // {:4d} SP=256'.format(self.nextpc))
        list.append('    @256')         # 0 : A=256
        list.append('    D=A')          # 1 : D=256
        list.append('    @SP')          # 2 : A=SP
        list.append('    M=D')          # 3 : RAM[SP]=256
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
            list.append('    @SP')          # 0 : A=SP
            list.append('    AM=M-1')       # 1 : A=RAM[SP]-1, RAM[SP]=RAM[SP]-1
            list.append('    D=M')          # 2 : D=RAM[RAM[SP]-1] : D=y
            list.append('    A=A-1')        # 3 : A=RAM[SP]-2 : M=x
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
            list.append('    @SP')          # 0 : A=SP
            list.append('    A=M-1')        # 1 : A=RAM[SP]-1 : M=y
            if   command == 'neg':
                list.append('    M=-M')     # 2 : -y
            elif command == 'not':
                list.append('    M=!M')     # 2 : !y
            self.nextpc += 3
        # --------------------------------------------------------
        elif command in ('eq', 'gt', 'lt'):
            list.append('    @SP')          # 0 : A=SP
            list.append('    AM=M-1')       # 1 : A=RAM[SP]-1, RAM[SP]=RAM[SP]-1
            list.append('    D=M')          # 2 : D=RAM[RAM[SP]-1] : D=x
            list.append('    A=A-1')        # 3 : A=RAM[SP]-2 : M=y
            list.append('    D=M-D')        # 4 : x-y
            list.append('    @JTRUE_{:03d}'.format(self.jumpID)) # 5 : 
            if   command == 'eq':
                list.append('    D;JEQ')    # 6 : x eq y then to 10
            elif command == 'gt':
                list.append('    D;JGT')    # 6 : x gt y then to 10
            elif command == 'lt':
                list.append('    D;JLT')    # 6 : x lt y then to 10
            list.append('    D=0')          # 7 : false
            list.append('    @JJOIN_{:03d}'.format(self.jumpID)) # 8 :
            list.append('    0;JMP')        # 9 : jump
            list.append('(JTRUE_{:03d})'.format(self.jumpID))
            list.append('    D=-1')         # 10 : true
            list.append('(JJOIN_{:03d})'.format(self.jumpID))
            list.append('    @SP')          # 11 : A=SP
            list.append('    A=M-1')        # 12 : A=RAM[SP]-1
            list.append('    M=D')          # 13 : RAM[RAM[SP]-1]=D
            self.jumpID += 1
            self.nextpc += 14
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
                list.append('    @{:d}'.format(int(index))) # 0 : A=index
                list.append('    D=A')      # 1 : D=index
                if   segment == 'local':    # 2 : A=base(LCL or ARG or THIS or THAT)
                    list.append('    @LCL')
                elif segment == 'argument':
                    list.append('    @ARG')
                elif segment == 'this':
                    list.append('    @THIS')
                elif segment == 'that':
                    list.append('    @THAT')
                list.append('    A=M+D')    # 3 : A=RAM[base]+index
                list.append('    D=M')      # 4 : D=RAM[RAM[base]+index]]
                list.append('    @SP')      # 5 : A=SP
                list.append('    A=M')      # 6 : A=RAM[SP]
                list.append('    M=D')      # 7 : RAM[RAM[SP]]=D
                list.append('    @SP')      # 8 : A=SP
                list.append('    M=M+1')    # 9 : RAM[SP]=RAM[SP]+1
                self.nextpc += 10
            elif segment in ('pointer', 'temp'):
                if   segment == 'pointer':
                    list.append('    @{:d}'.format(3+int(index)))   # 0 : A=3+index
                elif segment == 'temp':
                    list.append('    @{:d}'.format(5+int(index)))   # 0 : A=5+index
                list.append('    D=M')      # 1 : D=RAM[A]
                list.append('    @SP')      # 2 : A=SP
                list.append('    A=M')      # 3 : A=RAM[SP]
                list.append('    M=D')      # 4 : RAM[RAM[SP]]=D
                list.append('    @SP')      # 5 : A=SP
                list.append('    M=M+1')    # 6 : RAM[SP]=RAM[SP]+1
                self.nextpc += 7
            elif segment == 'constant':
                list.append('    @{:d}'.format(int(index))) # 0 : A=index
                list.append('    D=A')      # 1 : D=index
                list.append('    @SP')      # 2 : A=SP
                list.append('    A=M')      # 3 : A=RAM[SP]
                list.append('    M=D')      # 4 : RAM[RAM[SP]]=index
                list.append('    @SP')      # 5 : A=SP
                list.append('    M=M+1')    # 6 : RAM[SP]=RAM[SP]+1
                self.nextpc += 7
            elif segment == 'static':
                list.append('    @{:s}.{:d}'.format(self.vmname, int(index))) #  0 : A=index
                list.append('    D=M')      # 1 : D=RAM[index]
                list.append('    @SP')      # 2 : A=SP
                list.append('    A=M')      # 3 : A=RAM[SP]
                list.append('    M=D')      # 4 : RAM[RAM[SP]]=RAM[index]
                list.append('    @SP')      # 5 : A=SP
                list.append('    M=M+1')    # 6 : RAM[SP]=RAM[SP]+1
                self.nextpc += 7
            else:
                print "Error : undefined segment"
                sys.exit()
        # --------------------------------------------------------
        elif command == 'C_POP':
            if   segment in ('local', 'argument', 'this', 'that'):
                list.append('    @{:d}'.format(int(index))) # 0 : A=index
                list.append('    D=A')      # 1 : D=index
                if   segment == 'local':    # 2 : A=base(LCL or ARG or THIS or THAT)
                    list.append('    @LCL')
                elif segment == 'argument':
                    list.append('    @ARG')
                elif segment == 'this':
                    list.append('    @THIS')
                elif segment == 'that':
                    list.append('    @THAT')
                list.append('    D=D+M')    # 3 : D=index+RAM[base]
                list.append('    @R15')     # 4 : RAM[15]
                list.append('    M=D')      # 5 : RAM[15]=index+RAM[base]
                list.append('    @SP')      # 6 : A=SP
                list.append('    AM=M-1')   # 7 : A=RAM[SP]-1, RAM[SP]=RAM[SP]-1
                list.append('    D=M')      # 8 : D=RAM[RAM[SP]-1]
                list.append('    @R15')     # 9 : A=15
                list.append('    A=M')      # 0 : A=RAM[15]
                list.append('    M=D')      # 1 : RAM[RAM[15]]=RAM[RAM[SP]-1]
                self.nextpc += 12
            elif segment in ('pointer','temp'):
                list.append('    @SP')      # 0 : A=SP
                list.append('    AM=M-1')   # 1 : A=RAM[SP]-1, RAM[SP]=RAM[SP]-1
                list.append('    D=M')      # 2 : D=RAM[RAM[SP]-1]]
                if   segment == 'pointer':
                    list.append('    @{:d}'.format(3+int(index))) # 3 : A=3+index
                elif segment == 'temp':
                    list.append('    @{:d}'.format(5+int(index))) # 3 : A=5+index
                list.append('    M=D')      # 4 : RAM[A]=RAM[RAM[SP]-1]]
                self.nextpc += 5
            elif segment == 'constant':
                list.append('    @SP')      # 0 : A=SP
                list.append('    AM=M-1')   # 1 : A=RAM[SP]-1, RAM[SP]=RAM[SP]-1
                list.append('    D=M')      # 2 : D=RAM[RAM[SP]-1]]
                self.nextpc += 3
            elif segment == 'static':
                list.append('    @SP')      # 0 : A=SP
                list.append('    AM=M-1')   # 1 : A=RAM[SP]-1, RAM[SP]=RAM[SP]-1
                list.append('    D=M')      # 2 : D=RAM[RAM[SP]-1]]
                list.append('    @{:s}.{:d}'.format(self.vmname, int(index))) #  3 : A=index
                list.append('    M=D')      # 4 : RAM[index]=RAM[RAM[SP]-1]]
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
        list.append('    @SP')      # 0 : A=SP
        list.append('    AM=M-1')   # 1 : A=RAM[SP]-1, RAM[SP]=RAM[SP]-1
        list.append('    D=M')      # 2 : D=RAM[RAM[SP]-1]]
        list.append('    @{:s}'.format(label))  # 3 : A=label
        list.append('    D;JNE')    # 4 : if D=0 then goto A
        self.nextpc += 5
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def writeCall(self, functionName, numArgs):
        if self.debug: print "writeCall : ", functionName, numArgs
        list = []
        list.append('    // push return-address')
        list.append('    @{:s}$return{:d}'.format(functionName, self.uniqID))     # 0 : A=return_address
        list.append('    D=A')      # 1 : D=return_address
        list.append('    @SP')      # 2 : A=SP
        list.append('    A=M')      # 3 : A=RAM[SP]
        list.append('    M=D')      # 4 : RAM[RAM[SP]]=return_address
        self.incrementSP(list)      # +2
        list.append('    // push LCL')
        list.append('    @LCL')     # 7 : A=LCL
        list.append('    D=M')      # 8 : D=RAM[LCL]
        list.append('    @SP')      # 9 : A=SP
        list.append('    A=M')      # 0 : A=RAM[SP]
        list.append('    M=D')      # 1 : RAM[RAM[SP]]=RAM[LCL]
        self.incrementSP(list)      # +2
        list.append('    // push ARG')
        list.append('    @ARG')     # 4 : A=ARG
        list.append('    D=M')      # 5 : D=RAM[ARG]
        list.append('    @SP')      # 6 : A=SP
        list.append('    A=M')      # 7 : A=RAM[SP]
        list.append('    M=D')      # 8 : RAM[RAM[SP]]=RAM[ARG]
        self.incrementSP(list)      # +2
        list.append('    // push THIS')
        list.append('    @THIS')    # 1 : A=THIS
        list.append('    D=M')      # 2 : D=RAM[THIS]
        list.append('    @SP')      # 3 : A=SP
        list.append('    A=M')      # 4 : A=RAM[SP]
        list.append('    M=D')      # 5 : RAM[RAM[SP]]=RAM[THIS]
        self.incrementSP(list)      # +2
        list.append('    // push THAT')
        list.append('    @THAT')    # 8 : A=THAT
        list.append('    D=M')      # 9 : D=RAM[THAT]
        list.append('    @SP')      # 0 : A=SP
        list.append('    A=M')      # 1 : A=RAM[SP]
        list.append('    M=D')      # 2 : RAM[RAM[SP]]=RAM[THAT]
        self.incrementSP(list)      # +2
        list.append('    // ARG = SP - numArgs - 5')
        list.append('    @SP')      # 5 : A=SP
        list.append('    D=M')      # 6 : D=RAM[SP]
        list.append('    @{:d}'.format(int(numArgs)))   # 7 : A=numArgs
        list.append('    D=D-A')    # 8 : D=RAM[SP]-numArgs
        list.append('    @5')       # 9 : A=5
        list.append('    D=D-A')    # 0 : D=RAM[SP]-numArgs-5
        list.append('    @ARG')     # 1 : A=ARG
        list.append('    M=D')      # 2 : RAM[ARG]=RAM[SP]-numArgs-5
        list.append('    // LCL = SP')
        list.append('    @SP')      # 3 : A=SP
        list.append('    D=M')      # 4 : D=RAM[SP]
        list.append('    @LCL')     # 5 : A=LCL
        list.append('    M=D')      # 6 : RAM[LCL]=RAM[SP]
        list.append('    // goto {:s}'.format(functionName))
        list.append('    @{:s}'.format(functionName))   # 7 : A=functionName
        list.append('    0;JMP')    # 8 : goto functionName
        # return
        list.append('({:s}$return{:d})'.format(functionName, self.uniqID))
        self.uniqID +=1
        self.nextpc += 49
        self.funcname = ''
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def writeFunction(self, functionName, numLocals):
        if self.debug: print "writeFunction : ", functionName, numLocals
        list = []
        list.append('({:s})'.format(functionName))
        for i in range(int(numLocals)):
            list.append('    // init local val{:d}'.format(i))
            list.append('    @SP')      # 0 : A=SP
            list.append('    A=M')      # 1 : A=RAM[SP]
            list.append('    M=0')      # 2 : RAM[RAM[SP]]=0
            self.incrementSP(list)      # +2
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
        list.append('    // FRAME(R13) = LCL')
        list.append('    @LCL')     # 0 : A=LCL
        list.append('    D=M')      # 1 : D=RAM[LCL]
        list.append('    @R13')     # 2 : A=13
        list.append('    MD=D')     # 3 : RAM[13]=RAM[LCL], D=RAM[LCL]
        list.append('    // RET(R14) = *(FRAME-5)')
        list.append('    @5')       # 4 : A=5
        list.append('    A=D-A')    # 5 : A=RAM[LCL]-5
        list.append('    D=M')      # 6 : D=RAM[RAM[LCL]-5]] : return-address
        list.append('    @R14')     # 7 : A=R14
        list.append('    M=D')      # 8 : RAM[R14]=return-address
        list.append('    // *ARG = pop()')
        self.decrementSP(list)      # +2
        list.append('    A=M')      # 0 : A=RAM[SP-1]-1
        list.append('    D=M')      # 1 : D=RAM[RAM[SP]-1]
        list.append('    @ARG')     # 2 : A=ARG
        list.append('    A=M')      # 3 : A=RAM[ARG]
        list.append('    M=D')      # 4 : RAM[RAM[ARG]]=RAM[RAM[SP]-1]
        list.append('    // SP = ARG + 1')
        list.append('    @ARG')     # 7 : A=ARG
        list.append('    D=M+1')    # 8 : D=RAM[ARG]+1
        list.append('    @SP')      # 9 : A=SP
        list.append('    M=D')      # 0 : RAM[SP]=RAM[ARG]+1
        list.append('    // THAT = *(FRAME-1)')
        list.append('    @R13')     # 1 : A=13
        list.append('    D=M')      # 2 : D=RAM[13]
        list.append('    @1')       # 3 : A=1
        list.append('    A=D-A')    # 4 : A=RAM[13]-1
        list.append('    D=M')      # 5 : D=RAM[RAM[13]-1]
        list.append('    @THAT')    # 6 : A=THAT
        list.append('    M=D')      # 7 : RAM[THAT]=D
        list.append('    // THIS = *(FRAME-2)')
        list.append('    @R13')     # 8 : A=13
        list.append('    D=M')      # 9 : D=RAM[13]
        list.append('    @2')       # 0 : A=2
        list.append('    A=D-A')    # 1 : A=RAM[13]-2
        list.append('    D=M')      # 2 : D=RAM[RAM[13]-2]
        list.append('    @THIS')    # 3 : A=THIS
        list.append('    M=D')      # 4 : RAM[THIS]=D
        list.append('    // ARG = *(FRAME-3)')
        list.append('    @R13')     # 5 : A=13
        list.append('    D=M')      # 6 : D=RAM[13]
        list.append('    @3')       # 7 : A=3
        list.append('    A=D-A')    # 8 : A=RAM[13]-3
        list.append('    D=M')      # 9 : D=RAM[RAM[13]-3]
        list.append('    @ARG')     # 0 : A=ARG
        list.append('    M=D')      # 1 : RAM[ARG]=D
        list.append('    // LCL = *(FRAME-4)')
        list.append('    @R13')     # 2 : A=13
        list.append('    D=M')      # 3 : D=RAM[13]
        list.append('    @4')       # 4 : A=4
        list.append('    A=D-A')    # 5 : A=RAM[13]-4
        list.append('    D=M')      # 6 : D=RAM[RAM[13]-4]
        list.append('    @LCL')     # 7 : A=LCL
        list.append('    M=D')      # 8 : RAM[LCL]=D
        # goto RET
        list.append('    @R14')     # 9 : A=14
        list.append('    A=M')      # 0 : D=RAM[14]
        list.append('    0;JMP')    # 1 :
        self.nextpc += 52
        self.funcname = ''
        # output
        for code in list:
            if self.debug: print code
            self.asmfile.write(code+self.lfcode)
        if self.debug: print "nextpc : ", self.nextpc

    def incrementSP(self, list):
        list.append('    @SP')
        list.append('    M=M+1')

    def decrementSP(self, list):
        list.append('    @SP')
        list.append('    M=M-1')

    def openRAM(self, list, symbol):
        list.append('    @{:s}'.format(symbol))
        list.append('    A=M')


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
