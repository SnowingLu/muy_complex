import ply.lex as lex
import ply.yacc as yacc
class Stack:
  def __init__(self):
     self.items = []
  def isEmpty(self):
     return self.items == []
  def push(self,item):
     self.items.append(item)
  def pop(self):
     return self.items.pop()
  def peek(self):
     return self.items[len(self.items)-1]
  def size(self):
     return len(self.items)

def flat(r):
  res=[]
  for e in r:
      if isinstance (e,list):
          res.extend(flat(e))
      else:
          res.append(e)
  return res

def calcu(i,s1,s2):
   if i == '+':
       return s1+s2
   elif i == '-':
       return s1-s2
   elif i=='*':
       return s1*s2
   else:
       try: 
          return s1 /s2
       except ZeroDivisionError:
          print("0 cannot be denominator!")
          
          

def pre_cal(lis):
  pres=Stack()
  le=len(lis)
  fuhao=['+','-','*','/']
  for i in range(le-1,-1,-1):
      if lis[i] not in fuhao:
          pres.push(lis[i])
      else:
          s1=pres.pop()
          s2=pres.pop()
          re=calcu(lis[i],s1,s2)
          pres.push(re)
  return pres.pop()

tokens=('PLUS', 'MINUS','TIMES','DIVIDE','LPAREN','RPAREN','FLOAT','INT')
# tokens
t_PLUS=r'\+'
t_MINUS=r'-'
t_TIMES=r'\*'
t_DIVIDE=r'/'
t_LPAREN=r'\('
t_RPAREN=r'\)'
t_ignore = ' \t'
# number_integer, but can be float?
def t_FLOAT(t):
    r'\d+\.\d+'
    t.value=float(t.value)
    return t
def t_INT(t):
    r'\d+'
    t.value=int(t.value)
    return t

def t_error(t):
    print("Illegal character '%s'"%t.value[0])
    t.lexer.skip(1)

lexer=lex.lex()


precedence = (
        ('left','PLUS','MINUS'),
        ('left','TIMES','DIVIDE'),
        ('right','UMINUS'),
        )
 #return pre expression 
def p_expression(p):  
	'''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
	p[0]=[p[2],p[1],p[3]]

def p_expression_uminus(p): 
	'expression : MINUS expression %prec UMINUS'
	p[0]=['-',0,p[2]]

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_float(p):
        'expression : FLOAT'
        p[0] = p[1]

def p_expression_int(p):
    'expression : INT'
    p[0]=p[1]

def p_error(p):
	print("Syntax error at '%s'"% p.value)

parser = yacc.yacc()


while True:
  try:
    s=input('>please input an expression\n')
  except Exception:
    break
  r=parser.parse(s)
  print(r)
  lis=flat(r)
  print(lis)
  result=pre_cal(lis)
  print("result=",result)
  




