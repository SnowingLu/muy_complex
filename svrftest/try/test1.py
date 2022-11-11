from ply import *  # import everything from ply

# notice : string constant should be noticed because it can omit keyword influence
keywords=('ABUT', 'ACCUMULATE', 'ACUTE', 'ALL', 'ALSO', 'AND', 'ANGLE', 'ANGLED', 'APPEND', 'AREA', 'ATTACH', 'AUTO',
                'BY','BUMP', 'CAPACITANCE', 'CELL', 'COIN', 'COINCIDENT', 'CONNECT', 'CONNECTED', 'CONVEX','COLON',
                'COPY', 'CORNER', 'COS', 'COUNT', 'CUT', 'DATABASE', 'DATATYPE', 'DBCLASSIFY', 'DEANGLE', 'DENSITY', 
                'DEPTH', 'DEV', 'DEVICE', 'DFM', 'DIRECT', 'DISCONNECT', 'DONUT', 'DRAWN', 'DRC', 'EDGE',
                'ENC', 'ENCLOSURE', 'ERC', 'EXCLUDE', 'EXP', 'EXPAND','EXT', 'EXTEND', 'EXTENT', 'EXTENTS', 'EXTERNAL', 
                'FLAG', 'FLATTEN', 'FRACTURE', 'FRINGE','GOLDEN', 'GLOBALXY', 'GROUP','GROW', 
                'HCELL', 'HIER', 'HOLES', 'IN', 'INDUCTANCE', 'INSIDE', 'INT', 'INTERACT', 'INTERNAL', 'INTERSECTING', 
                'LABEL', 'LAYER', 'LAYOUT', 'LENGTH', 'LITHO', 'LOG', 'LVS', 'MAG', 'MAGNIFY', 'MAP', 'MASK', 
                'MAX', 'MAXIMUM', 'MEASURE', 'MERGE', 'MIN', 'MULTI', 'NAME', 'NET', 'NO', 'NODAL', 'NOHIER', 
                'NOMULTI', 'NONSIMPLE', 'NOPSEUDO', 'NOPUSH', 'NOT', 'NOTCH', 'EVEN','ODD',
                'OBTUSE', 'OF', 'OFFGRID', 'ONLY', 'OPCBIAS', 'OPCLINEEND', 'OPCSBAR', 'OPPOSITE', 'OR', 'ORDER',
                'ORNET', 'OUT', 'OUTSIDE', 'OVER', 'OVERLAP', 'PARA', 'PARALLEL', 'PARASITIC', 'PATH', 'PERC', 
                'PERIMETER', 'PERP', 'PERPENDICULAR', 'PEX', 'PINS', 'POLYGON', 'PORT', 'PORTS', 'POWER', 'PREC', 'PRECISION', 
                'PRIMARY', 'PROJ', 'PROJECTING', 'PROPERTY', 'PUSH', 'RATIO', 'RDB', 'RECTANGLE', 'RECTANGLES', 
                'REGION', 'REPLACE', 'REPORT', 'RESISTANCE', 'RESOLUTION', 'RET', 'ROTATE', 'RESULTS',
                'SBAR', 'SCALE', 'SCONNECT', 'SHIFT', 'SHRINK', 'SIN', 'SINGULAR', 'SIZE', 'SKEW', 'SNAP', 'SYSTEM',
                'SOURCE', 'SPACE', 'SPLIT', 'SQRT', 'SQUARE', 'SRAF_FILL', 'STAMP', 'STDIN','STEP', 'SUMMARY', 'SVRF', 
                'TAN', 'TDDRC', 'TEXT', 'TEXTTYPE', 'TITLE', 'TO','TOPEX', 'TOUCH', 'TRACE', 'TVF', 
                'UNIT', 'VARIABLE', 'VERTEX', 'VIRTUAL', 'WITH','WIDTH', 'XOR', 'YES','UNSATISFIED',
                'GDS', 'GDSII','GDS2', 'ASCII', 'SPICE', 'OASIS', 'LEFDEF', 'MILKYWAY', 'OPENACCESS', 'OA', 'CNET','BINARY',
                'CBLOCK','STRICT','PREFIX','INDEX','NOVIEW','USER','PSEUDO','TOP','MERGED','CHECK',
                'TEXTTAG','VERTICES','PROPERTIES','AUTOREF','AREF','PITCH','SUBSTITUTE','INCREMENTAL',
                'TRUNCATE','BACKUP','IGNORE','WRAP','ABSOLUTE','WINDOW','CENTERS','PRINT','CENTERED',
                'GRADIENT','MAGNITUDE','RELATIVE','COMBINE','CENTERLINE','FALSE','SHIELDED', 'FUNCTION','STRING','NUMBER',
                'OPPOSITE1','OPPOSITE2','EXTENDED','EXTENDED1', 'EXTENDED2','SYMMETRIC','FSYMMETRIC', 'ORTHOGONAL',
                'OVERUNDER','UNDEROVER','BEVEL','MAXANGLE','ENVIRONMENT'
                )
# a list of keywords in Page 58 of svrf rules, variable no case sensitivity, all to upper case
# more than p58 's table ,add if necessary

tokens= keywords+ ('RULECOMMENT', 'NEWLINE' ,  # only useful left
                    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN', 'POW', 'MODULUS', #+-*/ = ^ %
                    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', # KUOHAO
                    'EQ','LE', 'GE', 'NE', 'LT', 'GT',  'SEMICOLON',#comparison operator : ;
                    'FLOAT','INTEGER','ID',   'NEGATION','COMPLEMENT','COMMA',#basic elements
                     'STRINGS' ,'QMARK','COLONS' # elements like LAYOUT PATH "input.gds"  
                    )

t_PLUS = r'\+' 
t_MINUS= r'-'
t_TIMES= r'\*'
t_DIVIDE= r'/'
t_ASSIGN = r'='
t_POW = r'\^'
t_MODULUS = r'%'

t_LPAREN= r'\('
t_RPAREN= r'\)'
t_LBRACKET= r'\['
t_RBRACKET= r'\]'
t_LBRACE= r'\{'
t_RBRACE= r'\}'
t_SEMICOLON= r';'
t_COLONS=r':'
t_COMMA=r','
t_QMARK=r'\?'

t_EQ= '=='
t_LE = '<='
t_GE ='>='
t_NE = '!='
t_LT = '<'
t_GT ='>'
t_NEGATION=r'!'
t_COMPLEMENT=r'~'
t_ignore = ' \t'
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno+= len(t.value)
def t_multiline_comment(t):
    r'/\*(.|\n)*\*/'   # multiline can be accepted
    t.lexer.lineno += t.value.count('\n')
     # if multiline, lineno should be added 
def t_single_comment(t):
    r'//.*'
    pass

def t_RULECOMMENT(t):
    r'@.*' # @ in rule file, should return
    return t
def t_FLOAT(t):
    r'\d*\.\d+'
    t.value=float(t.value)
    return t
def t_INTEGER(t):
    r'\d+'
    t.value=int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9\._:\?]*'# look for variables' names, so need to search keywords
    TID=t.value.upper()# keywords are case-insensitive
    if TID in keywords:
        t.type=TID     # no longer t , but a keyword, so change it to a keyword
        t.value =TID
    return t    
def t_STRINGS(t):
    r'(\' ([^\n/]|/.)*?\')|(\" .*([^\n/]|/.)*?\")'     # path
    return t
    # 'xxx' or "xxx"  \ or /   why *?  -solved, ? as a constraint examples like 'a' 'b' if no ?, output as "'a' 'b'"
def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)
        
        
lexer=lex.lex()

import sys

if __name__ == '__main__':
    if len(sys.argv)==2:
        f=open(sys.argv[1]).read()
        lexer.input(f)
        for t in lexer:
            print(t)
        sys.exit()
    data=input(">")
    lexer.input(data)
    for t in lexer:
        print(t)
    
    