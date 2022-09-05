import lex1a 
from ply import *
tokens=lex1a.tokens

def p_rulefile(p):
    """rulefile : rulefile element
                | element"""
    if len(p) == 2:
        p[0] = []
        p[0].append(p[1])
    elif len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])

def p_semicolon_ele(p):
    'element : element SEMICOLON'
    p[0]=p[1]

def p_layer(p):
    'element : LAYER ID original_layer'
    p[0]={'command' : 'LAYER', 'name' : p[2], 'layers': p[3]}


def p_intid(p):
    ''' intid : INTEGER
                | ID '''
    p[0]=p[1]

def p_original_layers(p):
    """original_layer : original_layer intid
                            |  intid"""
    if len(p)==2:
        p[0]=[p[1]]       
    elif len(p)==3:
        p[0]=p[1]
        p[0].append(p[2])


def p_layers_result(p):
    'element : name ASSIGN layers_result'
    p[0]= p[3]
    p[0].update({'result': p[1]})


    
def p_boolean_operators(p):
    '''l_op : AND
              | OR
              | XOR
              | NOT'''
    p[0]=p[1]

def p_boolean_1(p):
    'layers_result : l_op layer_op layer_op'
    p[0] = {'command' : p[1], 'layers' : [p[2],p[3]]}
    
def p_boolean_2(p):
    'layers_result : layer_op l_op layer_op'
    p[0] = {'command' : p[2], 'layers' : [p[1],p[3]]}
    
def p_boolean_3(p):
    'layers_result : layer_op layer_op l_op'
    p[0] = {'command' : p[3], 'layers' : [p[1],p[2]]}

def p_layer_op_1(p):
    ' layer_op : name'
    p[0]=p[1]
    
def p_layer_op2(p):
    "layer_op : layer_paren"
    p[0]=p[1]

def p_paren_layers(p): 
    ' layer_paren : LPAREN layers_result RPAREN'
    p[0]=p[2]   

def p_name(p):
    ''' name : ID 
                 | STRING'''
    p[0] = p[1]
    








parser=yacc.yacc()

#da=input(">")
#p=parser.parse(da)
#print(p)
import yaml
import sys 
if __name__ == '__main__':
    if len(sys.argv)==3:
        da=open(sys.argv[1]).read()
        p = parser.parse(da)
        f = open(sys.argv[2], 'w')
        d = yaml.safe_dump(p)
        f.write(d)
        f.close()
        sys.exit(0)