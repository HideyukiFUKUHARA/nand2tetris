#!/usr/bin/env python
# coding: UTF-8

import re,sys

class JackTokenizer():

    debug=0     # 0:off, 1:print debug message
    lfcode = "\r\n"     # line feed code dos="\r\n", unix="\n"
    allkeyword=('class' , 'constructor' , 'function' , 'method' , 'field' , 'static' , 'var' ,
                'int' , 'char' , 'boolean' , 'void' , 'true' , 'false' , 'null' , 'this' ,
                'let' , 'do' , 'if' , 'else' , 'while' , 'return')

    def __init__(self, filename):
        self.alltoken = []
        prev_char = ''
        state = 'normal'
        data = ''
        #
        # romove all commnet
        #
        for line in open(filename, "r"):
            line = re.sub(r"\r\n", r"\n", line)     # cr+lf to lf
            line = re.sub(r"\[ \t].*", r"", line)   # del whitespace
            for char in line:
                if   state == 'normal':
                    if   char == '/':
                        state = 'comment_or_div'
                    elif char == '"':
                        data += char
                        state = 'string'
                    else:
                        if   char in ('{', '}', '(', ')', '[', ']', '.', ',',
                          ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'):
                            data += '\n' + char + '\n'
                        else:
                            data += char
                        state = 'normal'
                elif state == 'comment_or_div':
                    if   prev_char == '/' and char == '/' :
                        state = 'line_comment'
                    elif prev_char == '/' and char == '*' :
                        state = 'block_comment'
                    else:
                        data += '\n' + prev_char + '\n' + char
                        state = 'normal'
                elif state == 'line_comment':
                    if   char == '\n':
                        state = 'normal'
                elif state == 'block_comment':
                    if   prev_char == '*' and char == '/' :
                        state = 'normal'
                elif state == 'string':
                    data += char
                    if   prev_char != '\\' and char == '"' :
                        state = 'normal'
                else:
                    print "Error : illegal state"
                prev_char = char
        #
        # split token
        #
        data_len = len(data) - 1
        i = 0
        while i < data_len:
            # white space
            if re.match(r'[ \t]', data[i]):
                while re.match(r'[ \t]', data[i]) and i < data_len:
                    #sys.stdout.write("data[{:d}] = {:s}     whitespace\n".format(i, data[i]))
                    i += 1
            # return code
            elif data[i] == '\n':
                while data[i] == '\n' and i < data_len:
                    #sys.stdout.write("data[{:d}] =      return code\n".format(i))
                    i += 1
            # symbol
            elif data[i] in ('{', '}', '(', ')', '[', ']', '.', ',',
                          ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'):
                #sys.stdout.write("data[{:d}] = {:s}     symbol\n".format(i, data[i]))
                self.alltoken.append((1, data[i]))
                i += 1
            # integer
            elif re.match(r'[0-9]', data[i]):
                s = i
                while re.match(r'[0-9]', data[i]) and i < data_len:
                    #sys.stdout.write("data[{:d}] = {:s}     integer\n".format(i, data[i]))
                    i += 1
                self.alltoken.append((2, data[s:i]))
            # string
            elif data[i] == '"':
                #sys.stdout.write("data[{:d}] = {:s}     string\n".format(i, data[i]))
                s = i
                i += 1
                while data[i] != '"' and i < data_len:
                    #sys.stdout.write("data[{:d}] = {:s}     string\n".format(i, data[i]))
                    i += 1
                #sys.stdout.write("data[{:d}] = {:s}     string fin\n".format(i, data[i]))
                self.alltoken.append((3, data[s:i+1]))
                i += 1
            # keyword len2
            elif data[i:i+2] in ('do', 'if'):
                self.alltoken.append((0, data[i:i+2]))
                i += 2
            # keyword len3
            elif data[i:i+3] in ('var', 'int', 'let'):
                self.alltoken.append((0, data[i:i+3]))
                i += 3
            # keyword len4
            elif data[i:i+4] in ('char', 'void', 'true', 'null', 'this', 'else'):
                self.alltoken.append((0, data[i:i+4]))
                i += 4
            # keyword len5
            elif data[i:i+5] in ('class', 'field', 'false', 'while'):
                self.alltoken.append((0, data[i:i+5]))
                i += 5
            # keyword len6
            elif data[i:i+6] in ('method', 'static', 'return'):
                self.alltoken.append((0, data[i:i+6]))
                i += 6
            # keyword len7
            elif data[i:i+7] == 'boolean':
                self.alltoken.append((0, data[i:i+7]))
                i += 7
            # keyword len8
            elif data[i:i+8] == 'function':
                self.alltoken.append((0, data[i:i+8]))
                i += 8
            # keyword len11
            elif data[i:i+11] == 'constructor':
                self.alltoken.append((0, data[i:i+11]))
                i += 11
            # identifier
            elif re.match(r'[a-zA-Z_]', data[i]):
                s = i
                while re.match(r'[a-zA-Z_0-9]', data[i]) and data_len:
                    #sys.stdout.write("data[{:d}] = {:s}     identifier\n".format(i, data[i]))
                    i += 1
                self.alltoken.append((4, data[s:i]))
            else:
                print "Error : ???"
        #for i in self.alltoken: print i

    def hasMoreTokens(self):
        tmp = len(self.alltoken) > 0
        if self.debug: print "hasMoreTokens : ", tmp
        return tmp

    def advance(self):
        self.token = self.alltoken.pop(0)
        if self.debug: print "advance : ", self.token

    def tokenType(self):
        if self.token[0] == 0:
            tmp = 'KEYWORD'
        elif self.token[0] == 1:
            tmp = 'SYMBOL'
        elif self.token[0] == 2:
            tmp = 'INT_CONST'
        elif self.token[0] == 3:
            tmp = 'STRING_CONST'
        elif self.token[0] == 4:
            tmp = 'IDENTIFIER'
        else :
            print "Error : undefined token keyword"
        if self.debug: print "tokenType : ", tmp
        return tmp

    def keyWord(self):
        #tmp = self.token[1].upper()
        tmp = self.token[1]
        if self.debug: print "keyWord : ", tmp
        return tmp

    def symbol(self):
        tmp = self.token[1]
        if self.debug: print "symbol : ", tmp
        return tmp

    def identifier(self):
        tmp = self.token[1]
        if self.debug: print "identifier : ", tmp
        return tmp

    def intVal(self):
        tmp = self.token[1]
        if self.debug: print "intVal : ", tmp
        return tmp

    def stringVal(self):
        tmp = self.token[1]
        if self.debug: print "stringVal : ", tmp
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
        else                   :
            print "Error : undefined commnad"
            sys.exit()
        if self.debug: print "arg2 : ", tmp
        return tmp

    def write_all(self, filename):
        tokenfile = open (filename, 'w')
        tokenfile.write('<tokens>' + self.lfcode)
        while self.hasMoreTokens():
            self.advance()
            self.write(tokenfile, 2)
        tokenfile.write('</tokens>' + self.lfcode)
        tokenfile.close()

    def write(self, tokenfile, indent_num):
        tmp = self.tokenType()
        tokenfile.write(' ' * indent_num) 
        if tmp == 'KEYWORD':
            tokenfile.write('<keyword> ' + self.keyWord() + ' </keyword>' + self.lfcode)
        elif tmp == 'SYMBOL':
            tmp = self.symbol()
            if   tmp == '&': tmp = '&amp;'
            elif tmp == '>': tmp = '&gt;'
            elif tmp == '<': tmp = '&lt;'
            tokenfile.write('<symbol> ' + tmp + ' </symbol>' + self.lfcode)
        elif tmp == 'IDENTIFIER':
            tokenfile.write('<identifier> ' + self.identifier() + ' </identifier>' + self.lfcode)
        elif tmp == 'INT_CONST':
            tokenfile.write('<integerConstant> ' + self.intVal() + ' </integerConstant>' + self.lfcode)
        elif tmp == 'STRING_CONST':
            tokenfile.write('<stringConstant> ' + self.stringVal()[1:-1] + ' </stringConstant>' + self.lfcode)


# test
#J = JackTokenizer("Main.jack")
#J = JackTokenizer("Square.jack")
#J = JackTokenizer("SquareGame.jack")
#J.test()


