#!/usr/bin/env python

class code():

    def dest(self, data):
        tmp = 0
        for i in data:
            if   i == 'A': tmp += 4
            elif i == 'D': tmp += 2
            elif i == 'M': tmp += 1
        #print("dest : {:03b}".format(tmp))
        return tmp

    def comp(self, data):
        # a=0
        if   data == '0'  : tmp = 0b0101010
        elif data == '1'  : tmp = 0b0111111
        elif data == '-1' : tmp = 0b0111010
        elif data == 'D'  : tmp = 0b0001100
        elif data == 'A'  : tmp = 0b0110000
        elif data == '!D' : tmp = 0b0001101
        elif data == '!A' : tmp = 0b0110001
        elif data == '-D' : tmp = 0b0001111
        elif data == '-A' : tmp = 0b0110011
        elif data == 'D+1': tmp = 0b0011111
        elif data == 'A+1': tmp = 0b0110111
        elif data == 'D-1': tmp = 0b0001110
        elif data == 'A-1': tmp = 0b0110010
        elif data == 'D+A': tmp = 0b0000010
        elif data == 'D-A': tmp = 0b0010011
        elif data == 'A-D': tmp = 0b0000111
        elif data == 'D&A': tmp = 0b0000000
        elif data == 'D|A': tmp = 0b0010101
        # a=1
        elif data == 'M'  : tmp = 0b1110000
        elif data == '!M' : tmp = 0b1110001
        elif data == '-M' : tmp = 0b1110011
        elif data == 'M+1': tmp = 0b1110111
        elif data == 'M-1': tmp = 0b1110010
        elif data == 'D+M': tmp = 0b1000010
        elif data == 'D-M': tmp = 0b1010011
        elif data == 'M-D': tmp = 0b1000111
        elif data == 'D&M': tmp = 0b1000000
        elif data == 'D|M': tmp = 0b1010101
        #print("comp : {:07b}".format(tmp))
        return tmp

    def jump(self, data):
        if   data == 'JGT' : tmp = 0b001
        elif data == 'JEQ' : tmp = 0b010
        elif data == 'JGE' : tmp = 0b011
        elif data == 'JLT' : tmp = 0b100
        elif data == 'JNE' : tmp = 0b101
        elif data == 'JLE' : tmp = 0b110
        elif data == 'JMP' : tmp = 0b111
        else               : tmp = 0b000
        #print("jump : {:03b}".format(tmp))
        return tmp

    def test(self):
        self.dest("ADM")
        self.comp("D|M")
        self.jump("JEQ")

#c = code()
#c.test()

