# -*- coding: utf-8 -*-
from genereTreeGraphviz2 import printTreeGraph
 
reserved={
        'print':'PRINT',
        'if':'IF',
        'else':'ELSE',
        'while':'WHILE',
        'for':'FOR',
        'function':'FUNCTION',
        'return':'RETURN',
 
        }
 
tokens = [ 'NUMBER','MINUS', 'PLUS', 'PLUSPLUS', 'TIMES','DIVIDE', 'LPAREN',
          'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
          'EGALEGAL','INFEG', 'LACC', 'RACC', 'COMMA']+ list(reserved.values())
 
t_PLUS = r'\+' 
t_PLUSPLUS = r'\+\+'
t_MINUS = r'-' 
t_TIMES = r'\*' 
t_DIVIDE = r'/' 
t_LPAREN = r'\(' 
t_RPAREN = r'\)' 
t_OR = r'\|'
t_AND = r'\&'
t_SEMI = r';'
t_EGAL = r'\='
#t_NAME = r'[a-zA-Z_][a-zA-Z_0-9]*'
t_INF = r'\<'
t_SUP = r'>'
t_INFEG = r'\<\='
t_EGALEGAL = r'\=\='
t_LACC = r'\{'
t_RACC = r'\}'
t_COMMA = r','
 
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t
 
 
def t_NUMBER(t): 
    r'\d+' 
    t.value = int(t.value) 
    return t
 
t_ignore = " \t"
 
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
 
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
 
import ply.lex as lex
lex.lex()
 
names={}
functions = {}

precedence = ( 
        ('left','OR' ), 
        ('left','AND'), 
        ('nonassoc', 'INF', 'INFEG', 'EGALEGAL', 'SUP'), 
        ('left','PLUS', 'MINUS' ), 
        ('left','TIMES', 'DIVIDE'), 
        )
def p_start(p):
    'start : Linst'
    p[0] = ('PROG', ('fonctions', p[1][0]), ('main', p[1][1]))
    print(p[0])
    printTreeGraph(p[0])
    evalinst(p[0])

def p_Linst(p):
    '''Linst : Linst statement SEMI
        | statement SEMI'''
    if len(p) == 4 :
        # décomposition
        funcs, main = p[1]
        if is_function_def(p[2]): 
            p[0] = (('Inst', funcs, p[2]), main)
        else : 
            p[0] = (funcs, ('Inst', main, p[2]))
    else : 
        if is_function_def(p[1]):
            p[0] = (p[1], 'empty')
        else :
            p[0] = ('empty', p[1])

def p_bloc(p):
    '''bloc : bloc statement SEMI
    | statement SEMI'''
    if len(p) == 4:
        p[0] = ('bloc', p[1], p[2])
    else:
        p[0] = p[1]


def p_statement_function_whith_no_params(p):
    'statement : FUNCTION NAME LPAREN RPAREN LACC bloc RACC'
    p[0] = (p[2], ('params', 'empty'), ('Inst', p[6]))

def p_statement_function_whith_params(p):
    'statement : FUNCTION NAME LPAREN params RPAREN LACC bloc RACC'
    p[0] = (p[2], ('params', tuple(p[4])), ('Inst', p[7]))

def is_function_def(t):
    """Vérifie si un tuple est une définition de fonction"""
    return (isinstance(t, tuple) and len(t) >= 2 and 
            isinstance(t[1], tuple) and t[1][0] == 'params')

def p_params(p):
    '''params : params COMMA NAME
    | NAME'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN LACC bloc RACC'
    p[0] = ('if', p[3], p[6], None)

def p_statement_if_else(p):
    'statement : IF LPAREN expression RPAREN LACC bloc RACC ELSE LACC bloc RACC'
    p[0] = ('if', p[3], p[6], p[10])

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LACC bloc RACC'
    p[0] = ('while', p[3], p[6])

def p_statement_for(p):
    'statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LACC bloc RACC'
    p[0] = ('for', p[3], p[5], p[7], p[10])
 
def p_statement_expr(p): 
    'statement : PRINT LPAREN expression RPAREN'
    p[0] = ('print', p[3])

def p_statement_expr2(p):
    'statement : expression'
    p[0] = p[1]
 
def p_statement_assign(p):
    'statement : NAME EGAL expression'
    p[0] = ('assign', p[1], p[3])

# Grammaire pour appel de fonction
def p_expression_call(p):
    'expression : NAME LPAREN args RPAREN'
    p[0] = ('call', p[1], p[3])

def p_statement_args(p) :
    ''' args : args COMMA expression
        | expression
        | '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 :
        p[0] = [p[1]]
    else :
        p[0] = []
 
def p_expression_binop_inf(p): 
    'expression : expression INF expression' 
    p[0] = ('<', p[1], p[3])
 
def p_expression_binop_infEGAL(p): 
    'expression : expression INFEG expression' 
    p[0] = ('<=', p[1], p[3])
 
def p_expression_binop_sup(p): 
    'expression : expression SUP expression' 
    p[0] = ('>', p[1], p[3])
 
 
def p_expression_binop_egal(p): 
    'expression : expression EGALEGAL expression' 
    p[0] = ('==', p[1], p[3]) 
 
def p_expression_binop_and(p): 
    'expression : expression AND expression' 
    p[0] = ('and', p[1], p[3]) 
 
def p_expression_binop_or(p): 
    'expression : expression OR expression' 
    p[0] = ('or', p[1], p[3])
 
def p_expression_binop_plus(p): 
    'expression : expression PLUS expression' 
    p[0] = ('+', p[1], p[3])

def p_expression_binop_plusplus(p):
    'expression : expression PLUSPLUS'
    p[0] = ('++', p[1])
 
def p_expression_binop_times(p): 
    'expression : expression TIMES expression' 
    p[0] = ('*', p[1], p[3])
 
def p_expression_binop_divide_and_minus(p): 
    '''expression : expression MINUS expression 
     | expression DIVIDE expression''' 
    if p[2] == '-': p[0] = ('-', p[1], p[3])
    else : p[0] = ('/', p[1], p[3]) 
 
def p_expression_group(p): 
    'expression : LPAREN expression RPAREN' 
    p[0] = p[2] 
 
def p_expression_number(p): 
    'expression : NUMBER' 
    p[0] = p[1] 
 
def p_expression_name(p): 
    'expression : NAME' 
    p[0] = p[1]
 
def p_error(p):    print("Syntax error in input!")


def evalinst(tree):
    # print('evalinst de', tree)
    if tree == 'empty':
        return
    assert type(tree) is tuple
    if tree[0] == 'PROG':
        evalinst(tree[1])  # fonctions
        evalinst(tree[2])  # main
    elif tree[0] == 'fonctions':
        # Container de fonctions (pas une définition)
        evalinst(tree[1])
    elif tree[0] == 'main':
        evalinst(tree[1])
    elif tree[0] == 'Inst':
        evalinst(tree[1])
        evalinst(tree[2])
    elif tree[0] == 'bloc':
        evalinst(tree[1])
        evalinst(tree[2])
    elif tree[0] == 'print':
        print("CALC > ", evalexpr(tree[1]))
    elif tree[0] == 'assign':
        names[tree[1]] = evalexpr(tree[2])
    elif tree[0] == 'if':
        if evalexpr(tree[1]):
            print("[DEBUG] Branche IF")
            evalinst(tree[2])
        elif tree[3] is not None:
            print("[DEBUG] Branche ELSE")
            evalinst(tree[3])
    elif tree[0] == 'while':
        while evalexpr(tree[1]):
            evalinst(tree[2])
    elif tree[0] == '++':    
        evalexpr(tree) 
    elif tree[0] == 'for':
        evalinst(tree[1])
        while evalexpr(tree[2]) :
            evalinst(tree[4])
            evalinst(tree[3])
    elif is_function_def(tree):
        func_name = tree[0]
        func_params = tree[1][1]  # tree[1] = ('params', ...)
        func_bloc = tree[2][1] if tree[2][0] == 'Inst' else tree[2]

        functions[func_name] = (func_params, func_bloc)
        print(f"Fonction '{func_name}' définie")
    elif tree[0] == 'call':
        evalexpr(tree)
    


def evalexpr(tree):
    # print("evalexpr de ", tree)
    if type(tree) == int:
        return tree
    elif type(tree) == bool:
        return tree
    elif type(tree) == str:
        return names[tree]
    elif tree[0] == '+':
        return evalexpr(tree[1]) + evalexpr(tree[2])
    elif tree[0] == '*':
        return evalexpr(tree[1]) * evalexpr(tree[2])
    elif tree[0] == '/':
        return evalexpr(tree[1]) / evalexpr(tree[2])
    elif tree[0] == '-':
        return evalexpr(tree[1]) - evalexpr(tree[2])
    elif tree[0] == 'and':
        return evalexpr(tree[1]) and evalexpr(tree[2])
    elif tree[0] == 'or':
        return evalexpr(tree[1]) or evalexpr(tree[2])
    elif tree[0] == '<':
        return evalexpr(tree[1]) < evalexpr(tree[2])
    elif tree[0] == '<=':
        return evalexpr(tree[1]) <= evalexpr(tree[2])
    elif tree[0] == '==':
        return evalexpr(tree[1]) == evalexpr(tree[2])
    elif tree[0] == '>':
        return evalexpr(tree[1]) > evalexpr(tree[2])
    elif tree[0] == '++':
        var_name = tree[1]
        if type(var_name) != str:
            raise Exception("++ s'aplique que a des variables")
        if var_name not in names:
            raise Exception("Variable %s not defined" % tree[1])
        old_value = names[var_name]
        names[var_name] += 1
        return old_value
    elif tree[0] == 'call':
        func_name = tree[1]
        args_list = tree[2]  # Liste d'arguments

        if func_name not in functions:
            raise Exception(f"Fonction '{func_name}' undefine")

        print(f"Appel de la fonction '{func_name}' avec comme args'{args_list}'")

        func_params, func_body = functions[func_name]
        evalinst(func_body)

        return None

        
 
import ply.yacc as yacc
yacc.yacc()
# s = 'print(1+2);x=2+1;'
s = input('calc > ')
yacc.parse(s)