#!/usr/bin/env python

class symtbl():

    def __init__(self):
        self.dict = {}
        self.dict.update({
            'R0':0, 'R1':1, 'R2':2, 'R3':3, 'R4':4, 'R5':5, 'R6':6, 'R7':7,
            'R8':8, 'R9':9, 'R10':10, 'R11':11, 'R12':12, 'R13':13, 'R14':14, 'R15':15,
            'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4, 'SCREEN':0x4000, 'KBD':0x6000})

    def addEntry(self, symbol, address):
        self.dict.update({symbol:address})
        #print 'addEntry : ', symbol, address

    def contains(self, symbol):
        tmp = symbol in self.dict
        #print 'contains : ', tmp
        return tmp

    def getAddress(self, symbol):
        tmp = self.dict[symbol]
        #print 'getAddress : ', tmp
        return tmp

    def test(self):
        self.addEntry('hoge', 100)
        self.contains('hoge')
        self.getAddress('hoge')
        self.getAddress('KBD')

#s = symtbl()
#s.test()
