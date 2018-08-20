#!/usr/bin/env python
# coding: UTF-8

import sys,re,os,glob,subprocess

# 関数実行のポリシー
#   基本は関数実行前にはゴミデータが先頭にあることを前提とし、
#   advanceを実行することで該当データを取得できるようにする。
#   関数をネストする際に注意が必要。


class CompilationEngine():

    debug=1             # 0:off, 1:print debug message
    lfcode = "\r\n"     # line feed code dos="\r\n", unix="\n"
    indent_num=0
    unaryOp = ('-', '~')

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

    def compileClass(self):
        state = 'idle'
        while self.Tokenizer.hasMoreTokens():
            self.Tokenizer.advance()
            if self.debug: print "compileClass : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.Tokenizer.token_is('class'):
                    self.vmfile.write('<class>' + self.lfcode)
                    self.indent_inc()
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # class
                    state = 'name'
                else: self.exit('Error : compileClass idle')
            elif state == 'name':
                if self.Tokenizer.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # className
                    state = 'start_sym'
                else: self.exit('Error : compileClass name')
            elif state == 'start_sym':
                if self.Tokenizer.token_is('{'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # {
                    if self.Tokenizer.peek_next()[1] in ('static', 'field'):
                        self.compileClassVarDec()
                    elif self.Tokenizer.peek_next()[1] in ('constructor', 'function', 'method'):
                        self.compileSubroutine()
                    else:
                        self.exit('Error : compileClass start_sym keyword')
                else: self.exit('Error : compileClass start_sym {')
            elif state == 'end_sym':
                if self.Tokenizer.token_is('}'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # }
                    self.vmfile.write('</class>' + self.lfcode)
                    self.indent_dec()
                    state = 'idle'
                else: self.exit('Error : compileClass end_sym')

    def compileClassVarDec(self):
        state = 'idle'
        self.vmfile.write(' ' * self.indent_num + '<classVarDec>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileClassVarDec terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileClassVarDec : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                self.Tokenizer.write(self.vmfile, self.indent_num)      # static | field
                state = 'type'
            elif state == 'type':
                if self.Tokenizer.match_type():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # type
                    state == 'name'
                else: self.exit('Error : illegal class var declaretion')
            elif state == 'name':
                if self.Tokenizer.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # varName
                    state = 'name_continue'
                else: self.exit('Error : illegal class var name')
            elif state == 'name_continue':
                if self.Tokenizer.token_is(','):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # ,
                    state = 'name'
                elif self.Tokenizer.token_is(';'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # ;
                    state = 'finish'
                else: self.exit('Error : illegal class var name_continue')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</classVarDec>' + self.lfcode)

    def compileSubroutine(self):
        state = 'idle'
        self.vmfile.write(' ' * self.indent_num + '<subroutineDec>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileSubroutine terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileSubroutine : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                self.Tokenizer.write(self.vmfile, self.indent_num)      # constructor | function | method
                state = 'return_type'
            elif state == 'return_type':
                if self.Tokenizer.token_is('void') or self.Tokenizer.match_type():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # type
                    state = 'name'
                else: self.exit('Error : illegal subroutine type')
            elif state == 'name':
                if self.Tokenizer.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # subroutineName
                    state = 'paramlist'
                else: self.exit('Error : illegal subroutine name')
            elif state == 'paramlist':
                if self.Tokenizer.token_is('('):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # (
                    self.compileParameterList()                         # parameterList
                    state = 'paramlist_end'
                else: self.exit('Error : illegal subroutine (')
            elif state == 'paramlist_end':
                if self.Tokenizer.token_is(')'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # )
                    self.compileSubroutineBody()                        # subroutineBody
                    state = 'finish'
                else: self.exit('Error : compileSubroutine )')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</subroutineDec>' + self.lfcode)

    def compileParameterList(self):
        state = 'idle'
        self.vmfile.write(' ' * self.indent_num + '<parameterList>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileParameterList terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileParameterList : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.Tokenizer.token_is(')'):
                    self.Tokenizer.push((1, ')'))
                    state = 'finish'
                elif self.Tokenizer.match_type():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # type
                    state = 'name'
                else: self.exit('Error : illegal paramlist')
            elif state == 'name':
                if self.Tokenizer.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # varName
                    if self.Tokenizer.peek_next()[1] == ',':
                        state = 'continue'
                    elif self.Tokenizer.peek_next()[1] == ')':
                        state = 'finish'
                else: self.exit('Error : illegal identifier in paramlist')
            elif state == 'continue':
                self.Tokenizer.write(self.vmfile, self.indent_num)      # ,
                state = 'idle'
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</parameterList>' + self.lfcode)

    def compileSubroutineBody(self):
        state = 'idle'
        self.vmfile.write(' ' * self.indent_num + '<subroutineBody>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileSubroutineBody terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileSubroutineBody : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.Tokenizer.token_is('{'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # {
                    while self.Tokenizer.peek_next()[1] == 'var':
                        self.compileVarDec()                            # varDec*
                    self.compileStatements()                            # statements
                    state = 'end_body'
                else: self.exit('Error : illegal compileSubroutineBody idle {')
            elif state == 'end_body':
                if self.Tokenizer.token_is('}'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # }
                    state = 'finish'
                else: self.exit('Error : illegal compileSubroutineBody end_body }')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</subroutineBody>' + self.lfcode)

    def compileVarDec(self):
        state = 'idle'
        self.vmfile.write(' ' * self.indent_num + '<varDec>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileVarDec terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileVarDec : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.Tokenizer.token_is('var'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # var
                    state = 'type'
                else: self.exit('Error : illegal compileVarDec idle')
            elif state == 'type':
                if self.Tokenizer.match_type():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # type
                    state = 'var_name'
                else: self.exit('Error : illegal compileVarDec type')
            elif state == 'var_name':
                if self.Tokenizer.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # varName
                    state = 'continue'
                else: self.exit('Error : illegal compileVarDec name')
            elif state == 'continue':
                if self.Tokenizer.token_is(','):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # ,
                    state = 'var_name'
                elif self.Tokenizer.token_is(';'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # ;
                    state = 'finish'
                else: self.exit('Error : illegal compileVarDec continue')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</varDec>' + self.lfcode)

    def compileStatements(self):
        self.vmfile.write(' ' * self.indent_num + '<statements>' + self.lfcode)
        self.indent_inc()
        tmp = self.Tokenizer.peek_next()[1]
        if self.debug: print "compileStatements : ", tmp
        if   tmp == 'let'   : self.compileLet()
        elif tmp == 'if'    : self.compileIf()
        elif tmp == 'while' : self.compileWhile()
        elif tmp == 'do'    : self.compileDo()
        elif tmp == 'return': self.compileReturn()
        else: self.exit('Error : illegal compileStatements let | if | while | do | return')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</statements>' + self.lfcode)


    def compileDo(self):
        pass

    def compileLet(self):
        state = 'keyword'
        self.vmfile.write(' ' * self.indent_num + '<letStatement>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileLet terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileLet : ", state, self.Tokenizer.token[1]
            if state == 'keyword':
                if self.Tokenizer.token_is('let'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # let
                    state = 'name'
                else: self.exit('Error : compileLet let')
            elif state == 'name':
                if self.Tokenizer.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # varName
                    state = 'array_expr_start'
                else: self.exit('Error : compileLet name')
            elif state == 'array_expr_start':
                if self.Tokenizer.token_is('['):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # [
                    self.compileExpression()                            # expression
                    state = 'array_end'
                elif self.Tokenizer.token_is('='):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # =
                    self.compileExpression()                            # expression
                    state = 'expr'
                else: self.exit('Error : compileLet array_expr_start')
            elif state == 'array_end':
                if self.Tokenizer.token_is(']'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # ]
                    state = 'expr_start'
                else: self.exit('Error : compileLet array_end ]')
            elif state == 'expr_start':
                if self.Tokenizer.token_is('='):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # =
                    self.compileExpression()                            # expression
                    state = 'expr_end'
                else: self.exit('Error : compileLet expr_start')
            elif state == 'expr_end':
                if self.Tokenizer.token_is(';'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # ;
                    state = 'finish'
                else: self.exit('Error : compileLet expr_end')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</letStatement>' + self.lfcode)

    def compileWhile(self):
        pass

    def compileReturn(self):
        pass

    def compileIf(self):
        pass

    def compileExpression(self):
        state = 'term'
        self.vmfile.write(' ' * self.indent_num + '<expression>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileExpression terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileExpression : ", state, self.Tokenizer.token[1]
            if state == 'term':
                self.Tokenizer.push(self.Tokenizer.token)
                self.compileTerm()
                if self.Tokenizer.peek_next()[1] in self.unaryOp:
                    state = 'op'
                else:
                    state = 'finish'
            elif state == 'op':
                if self.Tokenizer.match_op():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # op
                    self.Tokenizer.push(self.Tokenizer.token)
                    self.compileTerm()
                    state = 'op'
                else:
                    state = 'finish'
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</expression>' + self.lfcode)

    def compileTerm(self):
        state = 'idle'
        self.vmfile.write(' ' * self.indent_num + '<term>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileTerm terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileTerm : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.Tokenizer.is_integer():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # integerConstant
                    state = 'finish'
                elif self.Tokenizer.is_string():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # stringConstant
                    state = 'finish'
                elif self.Tokenizer.is_keyword():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # keyword
                    state = 'finish'
                elif self.Tokenizer.token_is('('):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # (
                    state = 'expr'
                elif self.Tokenizer.token_is(self.unaryOp):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # unaryOp
                    state = 'term'
                elif self.Tokenizer.peek_next()[1] in ('(', '.'):
                    self.Tokenizer.push(self.Tokenizer.token)
                    self.compileSubroutineCall()                        # subroutineCall
                elif self.Tokenizer.peek_next()[1] == '[':
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # varName[]
                    state = 'varname_array'
                else:
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # varName
                    state = 'finish'
            elif state == 'expr':
                self.compileExpression()
                state = 'expr_end'
            elif state == 'varname_array':
                self.compileExpression()
                state = 'varname_array_end'
            elif state == 'expr_end':
                if self.Tokenizer.token_is(')'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # )
                    state = 'finish'
                else:
                    self.exit('Error : compileTerm expr_end')
            elif state == 'varname_array_end':
                if self.Tokenizer.token_is(']'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # )
                    state = 'finish'
                else:
                    self.exit('Error : compileTerm varname_array_end')
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</term>' + self.lfcode)

    def compileSubroutineCall(self):
        state = 'idle'
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileSubroutineCall terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileSubroutineCall : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.Tokenizer.is_identifier():
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # subroutineName | className | varName
                    state = 'second'
                else: self.exit('Error : compileSubroutineCall idle')
            elif state == 'second':
                if self.Tokenizer.token_is('.'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # .
                    state = 'name'
                elif self.Tokenizer.token_is('('):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # (
                    state = 'exprlist'
                else: self.exit('Error : compileSubroutineCall second')
            elif state == 'name':
                self.Tokenizer.write(self.vmfile, self.indent_num)  # Name
                state = 'after_name'
            elif state == 'after_name':
                if self.Tokenizer.token_is('('):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # (
                    self.compileExpressionList()                        # expressionList
                    state = 'exprlist_end'
                else: self.exit('Error : compileSubroutineCall after_name (')
            elif state == 'exprlist_end':
                if self.Tokenizer.token_is(')'):
                    self.Tokenizer.write(self.vmfile, self.indent_num)  # )
                    state = 'finish'
                else: self.exit('Error : compileSubroutineCall exprlist_end')

    def compileExpressionList(self):
        state = 'idle'
        self.vmfile.write(' ' * self.indent_num + '<expressionList>' + self.lfcode)
        self.indent_inc()
        while state != 'finish':
            if not self.Tokenizer.hasMoreTokens(): self.exit('Error : compileExpressionList terminate')
            self.Tokenizer.advance()
            if self.debug: print "compileExpressionList : ", state, self.Tokenizer.token[1]
            if state == 'idle':
                if self.Tokenizer.token_is(')'):
                    self.Tokenizer.push(self.Tokenizer.token)
                    state = 'finish'
                else:
                    self.Tokenizer.push(self.Tokenizer.token)
                    self.compileExpression()
                    state = 'idle'
        self.indent_dec()
        self.vmfile.write(' ' * self.indent_num + '</expressionList>' + self.lfcode)

    def close(self):
        self.vmfile.close()

    def test(self):
        self.vmfile.write('abc123')
        self.close()

# test
#c = CompilationEngine("hage.xml")
#c.test()



