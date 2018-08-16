#!/usr/bin/env python
# coding: UTF-8

import sys,re,os,glob


class CompilationEngine():

    debug=1             # 0:off, 1:print debug message
    lfcode = "\r\n"     # line feed code dos="\r\n", unix="\n"
    indent_num=0

    def __init__(self, filename, JackTokenizer):
        self.vmfile = open(filename, 'w')
        self.Tokenizer = JackTokenizer

    def exit(self, message):
        print message
        sys.exit()

    def indent_inc(self):
        self.indent_num += 2

    def indent_dec(self):
        self.indent_num -= 2

    def is_keyword(self):
        if self.Tokenizer.token[0] == 0: return 1
        else : return 0

    def is_symbol(self):
        if self.Tokenizer.token[0] == 1: return 1
        else : return 0

    def is_integer(self):
        if self.Tokenizer.token[0] == 2: return 1
        else : return 0

    def is_string(self):
        if self.Tokenizer.token[0] == 3: return 1
        else : return 0

    def is_identifier(self):
        if self.Tokenizer.token[0] == 4: return 1
        else : return 0

    def match_type(self):
        if self.Tokenizer.token[1] in ('int', 'char', 'boolean'): return 1
        elif self.is_identifier(): return 1
        else: return 0

    def token_is(self, list):
        if self.Tokenizer.token[1] in list: return 1
        else: return 0


    def compileClass(self):
        state = 'idle'
        while self.Tokenizer.hasMoreTokens():
            self.Tokenizer.advance()
            if self.debug: print "compileClass : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.token_is('class'):
                    self.vmfile.write('<class>' + self.lfcode)
                    self.indent_inc()
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'name'
                else:
                    self.exit('Error : not exist a class declaration')
            elif state == 'name':
                if self.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'start_sym'
                else:
                    self.exit('Error : not exist a class name')
            elif state == 'start_sym':
                if self.token_is('{'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'body'
                else:
                    self.exit('Error : not exist {')
            elif state == 'body':
                if self.token_is(('static', 'field')):
                    self.compileClassVarDec()
                elif self.token_is(('constructor', 'function', 'method')):
                    self.compileSubroutine()
                elif self.token_is('}'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    self.vmfile.write('</class>' + self.lfcode)
                    self.indent_dec()
                    state = 'idle'
                else:
                    self.exit('Error : not exist classVarDec or subroutineDec or {')

    def compileClassVarDec(self):
        state = 'type'
        self.vmfile.write(' ' * self.indent_num + '<classVarDec>' + self.lfcode)
        self.indent_inc()
        self.Tokenizer.write(self.vmfile, self.indent_num)  # static | field
        while self.Tokenizer.hasMoreTokens():
            self.Tokenizer.advance()
            if state == 'type':
                if self.match_type():
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state == 'name'
                else:
                    self.exit('Error : illegal class var declaretion')
            elif state == 'name':
                if self.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'name2'
                else:
                    self.exit('Error : illegal class var name')
            elif state == 'name2':
                if self.token_is(','):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'name'
                elif self.token_is(';'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    break
                else:
                    self.exit('Error : illegal class var name2')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</classVarDec>' + self.lfcode)


    def compileSubroutine(self):
        state = 'return_type'
        self.vmfile.write(' ' * self.indent_num + '<subroutineDec>' + self.lfcode)
        self.indent_inc()
        self.Tokenizer.write(self.vmfile, self.indent_num)  # constructor | function | method
        while self.Tokenizer.hasMoreTokens():
            self.Tokenizer.advance()
            if self.debug: print "compileSubroutine : ", state, self.Tokenizer.token[1]
            if state == 'return_type':
                if self.token_is('void') or self.match_type():
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'name'
                else:
                    self.exit('Error : illegal subrutine type')
            elif state == 'name':
                if self.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'param'
                else:
                    self.exit('Error : illegal subrutine name')
            elif state == 'param':
                if self.token_is('('):
                    self.compileParameterList()
                    state = 'body_start'
                else:
                    self.exit('Error : illegal subrutine (')
            elif state == 'body_start':
                self.vmfile.write(' ' * self.indent_num + '<subroutineBody>' + self.lfcode)
                self.indent_inc()
                if self.token_is('{'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'var'
                else:
                    self.exit('Error : illegal subrutine paramlist')
            elif state == 'var':
                if self.token_is('var'):
                    self.vmfile.write(' ' * self.indent_num + '<varDec>' + self.lfcode)
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'var_type'
                else:
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'statements'
            elif state == 'var_type':
                if self.match_type():
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'var_name'
                else:
                    self.exit('Error : illegal subrutine paramlist')
            elif state == 'var_name':
                if self.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'var_term'
                else:
                    self.exit('Error : illegal subrutine paramlist')
            elif state == 'var_term':
                if self.token_is(','):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'var_type'
                elif self.token_is(';'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'var'
                else:
                    self.exit('Error : illegal subrutine paramlist')
            elif state == 'var_term':
                if self.token_is(','):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'var_type'
                elif self.token_is(';'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)
                    state = 'var'
                else:
                    self.exit('Error : illegal subrutine paramlist')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</subroutineDec>' + self.lfcode)


    def compileParameterList(self):
        state = 'idle'
        self.Tokenizer.write(self.vmfile, self.indent_num)  # (
        self.vmfile.write(' ' * self.indent_num + '<parameterList>' + self.lfcode)
        self.indent_inc()
        while self.Tokenizer.hasMoreTokens():
            self.Tokenizer.advance()
            if self.debug: print "compileParameterList : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.token_is(')'):
                    break
                else:
                    self.exit('Error : illegal paramlist')
            # TODO
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</parameterList>' + self.lfcode)
        self.Tokenizer.write(self.vmfile, self.indent_num)

    def compileVarDec(self):
        pass

    def compileStatements(self):
        pass

    def compileDo(self):
        pass

    def compileLet(self):
        pass

    def compileWhile(self):
        pass

    def compileReturn(self):
        pass

    def compileIf(self):
        pass

    def compileExpression(self):
        pass

    def compileTerm(self):
        pass

    def compileExpressionList(self):
        pass

    def close(self):
        self.vmfile.close()

    def test(self):
        self.vmfile.write('abc123')
        self.close()

# test
#c = CompilationEngine("hoge.xml")
#c.test()



