from ply import *
import test1
import yaml,sys

tokens=test1.tokens

precedence = (
        ('left','PLUS','MINUS'),   
        ('left','TIMES','DIVIDE','POW','MODULUS'),  
        ('right','UMINUS','NEGATION'),         
        )

class env:
    def __init__(self, name = None):
        self.name = name
        self.temp_id = 0
        self.gen = []
        self.results = []
        pass

    def gentemp(self):
        self.temp_id += 1
        strid = "temp_id<%s>" % self.temp_id
        if self.name:
            strid = self.name + "::" + strid
        return strid

    def add_result(self, result):
        self.results.append(result)

envstack = []

top = env()

def gentemp():
    global top 
    return top.gentemp()

def add_result(result):
    global top
    top.add_result(result)

def gencode(p):
    global top
    top.gen.append(p)

def saveenv(name):
    global top
    global envstack
    envstack.append(top)
    top = env(name)

def loadenv():
    global top
    global envstack
    top = envstack.pop()

#rule file
def p_rulefile(p):
    """rulefile : rulefile element
                | element"""
    if len(p) == 2:
        p[0] = []
        p[0].append(p[1])
        gencode(p[1])
    elif len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])
        gencode(p[2])
        
#element define
def p_element_semi(p):
    """element : element SEMICOLON"""
    p[0] = p[1]

def p_element_kinds(p):
    """element : connect_stmts
                    | layer_map_stmts
                    | drc_stmts
                    | layout_stmt
                    | flag_stmt
                    | text_stmt"""
    p[0] = p[1]


def p_element_layer_operation(p):
    """element : layer_operation"""
    result = gentemp()
    add_result(result)
    p[0] = p[1]
    p[0].update({'result': result})
    
def p_element_global_layer_definition(p):
    """element : name ASSIGN layer_operation"""
    result = {'result' : p[1]}
    p[0] = p[3]
    p[0].update(result)

#layer assignment
def p_element_layer_assignment(p):
    """element : LAYER name layer_set"""
    p[0] = {'command': 'LAYER', 'name' : p[2], 'layers' : p[3]}

def p_layer_set(p):
    """layer_set : layer_set INTEGER
                 | layer_set name
                 | INTEGER
                 | name"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])
        

####### layer map #######
def p_layer_map_statement(p): 
    '''layer_map_stmts : LAYER MAP source_layer DATATYPE source_type INTEGER
               | LAYER MAP source_layer TEXTTYPE source_type INTEGER
               | LAYER MAP source_layer TEXTTYPE source_type INTEGER INTEGER'''
    if len(p)==7:
        p[0] = { 'config' : 'LAYER MAP', 'type' : p[4], 'source_layer' : p[3],'source_type':p[5], 'target_layer' : p[6]}
    elif len(p)==8:
        p[0] = { 'config' : 'LAYER MAP', 'type' : p[4], 'source_layer' : p[3],'source_type':p[5], 'target_layer' : p[6],'target_texttype' : p[7]}

def p_source_layer(p):
    ''' source_layer : INTEGER
                            | constraints'''
    p[0] = p[1]
def p_source_type(p):
    ''' source_type : INTEGER
                            | constraints'''
    p[0] = p[1]


###################
####   rule check    ####
###################
def p_enter_rule_check(p):
    """enter_rule_check : name LBRACE"""
    p[0] = {'name' : p[1]}
    saveenv(p[1])

def p_leave_rule_check(p):
    """leave_rule_check : RBRACE"""
    global top
    p[0] = [top.gen, top.results]
    loadenv()

def p_element_rule_check(p):
    """element : enter_rule_check rulecheckbody leave_rule_check"""
    p[0] = {'command' : 'RULE', 'block' : p[3][0], 'results': p[3][1]}
    p[0].update(p[1])

def p_rule_check_body_empty(p):
    """rulecheckbody : empty"""
    p[0] = []

def p_rule_check_body(p):
    """rulecheckbody : rulecheckbody element"""
    p[0] = p[1]
    p[0].append(p[2])
    gencode(p[2])

def p_rule_comment(p):
    """element : RULECOMMENT"""
    p[0] = {'command' : 'RULECOMMENT', 'content' : p[1]}


#### flag ####
def p_flag_nonsimple(p):
    """flag_stmt : FLAG NONSIMPLE YES
                      | FLAG NONSIMPLE NO"""
    p[0] = {'config' : 'FLAG NONSIMPLE', 'switch' : p[3]}

#########      LAYOUT      #########
def p_layout_path(p):
    ' layout_stmt : LAYOUT PATH path_ops'
    p[0]={'config': 'LAYOUT PATH', 'files' :p[3]}

def p_path_ops(p):
    ''' path_ops : STDIN
                      | file_name_op
                      | path_ops file_name_op'''
    if len(p)==2:
        p[0]=[p[1]]
    else:
        p[0]=p[1]
        p[0].append(p[2])

def p_file_name_ops(p):
    ' file_name_op :  name file_ops'
    p[0]={'filename' : p[1], 'options' : p[2]}
 
def p_file_ops_empty(p):
    ' file_ops : empty'
    p[0]=[]   
def p_file_ops(p):
    ''' file_ops : file_ops bumps
                    | file_ops magops
                    | file_ops precops
                    | file_ops GOLDEN'''
    p[0]=p[1]
    p[0].append(p[2])
    
def p_bumps(p):
    ' bumps : BUMP number'
    p[0]={'BUMP' : p[2]}
def p_mag_ops(p):
    ''' magops : MAG number
                    | MAG AUTO'''
    p[0]={'MAG' : p[2]}
def p_prec_ops(p):
    ''' precops : PREC number
                     | PREC INTEGER INTEGER'''
    if len(p)==3:
        p[0]={'PREC' : p[2]}
    elif len(p)==4:
        p[0]={'PREC' : p[2]/p[3]}

########    text    ########
def p_stmt_text(p):
    ''' text_stmt : TEXT number number
                    | TEXT name number number layer_single'''  # last name should be layer
    if len(p)==4:
        p[0]={'config' : 'TEXT', 'coordinate_pair':[p[2],p[3]]}
    elif len(p)==6:
        p[0]={'config' : 'TEXT', 'coordinate_pair':[p[3],p[4]], 'text_name' : p[2], 'layer' : p[5]}


###### variable ######

def p_variable(p):
    ''' element : VARIABLE name value values
                    | VARIABLE name ENVIRONMENT   '''
    if len(p)==4:
        p[0]={'command': p[1], 'out1':p[2], 'value':p[3]}
    else:
        a=p[4]
        a.append(p[3])
        p[0]={'command':p[1],'out1':p[2],'value': a}
        
    
def p_vari_values(p):
    ''' values : values value
                    | empty'''
    if len(p)<3:
        p[0]=[]
    else:
        p[0]=p[1]
        p[0].append(p[2])
def p_vari_value(p):
    ''' value : number'''
    p[0]=p[1]

########     DRC     #########
def p_drc_results_database(p):
    ' drc_stmts : DRC RESULTS DATABASE name drd_format drd_ops'
    p[0] = {'config' : 'DRC RESULTS DATABASE', 'filename' :p[4], 'format' : p[5], 'options': p[6]}

def p_drd_format(p):
    ''' drd_format : ASCII
                            | GDSII
                            | GDS
                            | GDS2
                            | OASIS
                            | BINARY'''
    p[0]=p[1] 
def p_drd_format_default(p):
    ' drd_format : empty'
    p[0]='ASCII'  
def p_drd_ops_empty(p):
    ' drd_ops : empty'
    p[0]=[]
def p_drd_ops(p):
    ''' drd_ops : drd_ops CBLOCK
                    | drd_ops STRICT
                    | drd_ops PREFIX name
                    | drd_ops APPEND name
                    | drd_ops drc_op1
                    | drd_ops drc_op2'''
    p[0]=p[1]
    if len(p)==3:
        p[0].append(p[2])
    else:
        p[0].append({p[2]: p[3]})        
def p_drc_op1(p):
    ''' drc_op1 : INDEX
                    | INDEX NOVIEW'''
    p[0]=' '.join(p[1:])
def p_drc_op2(p):
    ''' drc_op2 : USER MERGED
                    | PSEUDO
                    | USER
                    | TOP'''
    p[0]=' '.join(p[1:])
    
    
def p_drc_check_map(p):    
    ' drc_stmts : DRC CHECK MAP name dcm_ops'
    p[0]={'config': 'DRC CHECK MAP', 'rule_check' : p[4], 'options' : p[5]}

def p_drc_check_map_ops1(p):
    'dcm_ops : dcm_ops name'
    p[0]=p[1]
    p[0].append({'filename': p[2]})        
def p_drc_check_map_ops234(p):
    ''' dcm_ops : dcm_ops MAG number
                        | dcm_ops drc_op1
                        | dcm_ops drc_op2
                        | dcm_ops TEXTTAG name
                        | dcm_ops PREC number
                        | dcm_ops PREFIX name
                        | dcm_ops APPEND name
                        | dcm_ops MAXIMUM RESULTS INTEGER
                        | dcm_ops MAXIMUM RESULTS ALL
                        | dcm_ops MAXIMUM VERTICES INTEGER
                        | dcm_ops MAXIMUM VERTICES ALL
                        | dcm_ops dcm_format'''
    p[0]=p[1]
    if len(p)==3:
        p[0].append(p[2])
    elif len(p)==4:
        p[0].append({p[2]:p[3]})
    elif len(p)==5:
        p[0].append({' '.join(p[2:3]): p[4]})                        
def p_drc_check_map_empty(p):
    ' dcm_ops : empty'
    p[0]=[]

def p_dcm_format1(p):
    ''' dcm_format1 : gdses 
                            | gdses INTEGER
                            | gdses INTEGER INTEGER
                            | OASIS
                            | OASIS INTEGER
                            | OASIS INTEGER INTEGER
                            | ASCII
                            | BINARY'''
    if len(p)==2:
        p[0]={p[1] : [] }
    else:
        p[0]={p[1] : [p[2:]]}
def p_dcm_format(p):
    ''' dcm_format : dcm_format1
                         | dcm_format1 PROPERTIES'''
    if len(p)==2:
        p[0]=p[1]
    else:
        p[0]=p[1]
        p[0].update({'PROPERTIES':1})
                         
def p_gdses(p):
    '''gdses : GDS
                | GDSII
                | GDS2'''
    p[0]=p[1]
def p_drc_check_map_ops5(p):
    ' dcm_ops : dcm_ops drc_refs'
    p[0]=p[1]
    p[0].append(p[2])    
def p_drc_refs(p):
    ''' drc_refs : AUTOREF
                    | AUTOREF name
                    | AREF name number number aref_ops
                    | AREF name number number INTEGER aref_ops'''
    if len(p)==2:
        p[0]=p[1]
    elif len(p)==3:
        p[0]={'AUTOREF': p[2]}
    elif len(p)==6:
        p[0]={ 'AREF' :p[2], 'width' :p[3],'length':p[4]}
        p[0].update(p[5])
    elif len(p)==7:
        p[0]={ 'AREF' :p[2], 'width' :p[3],'length':p[4], 'min_element_count':p[5]}
        p[0].update(p[6])
        
def p_aref_ops_empty(p):
    ' aref_ops : empty'
    p[0]={}
def p_aref_ops(p):
    ''' aref_ops : aref_ops MAXIMUM PITCH number
                    | aref_ops SUBSTITUTE num_pairs '''
    if len(p)==5:
        p[0]=p[1]
        p[0].update({'MAXIMUM PITCH' : p[4]})
    else:
        p[0]=p[1]
        p[0].update({'SUBSTITUTE' : p[3:]})
def p_num_pairs(p):
    ''' num_pairs : num_pairs number number
                        | number number'''
    if len(p)==3:
        p[0]=[tuple(p[1:])]
    else:
        p[0]=p[1]
        p[0].append(tuple(p[2:]))
        
        
def p_drc_incremental_connect(p):
    ''' drc_stmts : DRC INCREMENTAL CONNECT YES
                        | DRC INCREMENTAL CONNECT NO'''
    p[0]={'config': 'DRC INCREMENTAL CONNECT', 'switch' :p[4]}
    

######   layer operations basic  ########

def p_implicit_layer(p):
    """implicit_layer : LPAREN layer_operation RPAREN"""
    tmpid = gentemp()
    p[0] = tmpid

    result = {'result' : tmpid}
    p[2].update(result)
    gencode(p[2])

def p_layer_single(p):
    """layer_single : implicit_layer"""
    p[0] = p[1]

def p_layer_single2(p):
    """layer_single : name"""
    p[0] = p[1]
# from error layer to edge layer --- notation
def p_layer_positive(p):
    """layer_single : LBRACKET layer_single RBRACKET"""
    p[0] = {'edge_output_option' : 'positive', 'name' : p[2]}

def p_layer_negative(p):
    """layer_single : LPAREN layer_single RPAREN"""
    p[0] = {'edge_output_option' : 'negative', 'name' : p[2]}



##### single layer operations (no other ops)####
def p_single_layer_op(p):
    """single_layer_op : AREA
                                | ANGLE
                                | LENGTH """
    p[0] = ' '.join(p[1:])

def p_layer_op_single(p):
    """layer_operation : single_layer_op layer_single constraints"""
    p[0] = {'command' : p[1], 'layer' : p[2], 'constraints' : p[3]}
def p_layer_op_single2(p):
    """layer_operation : layer_single single_layer_op constraints"""
    p[0] = {'command' : p[2], 'layer' : p[1], 'constraints' : p[3]}
def p_layer_op_single3(p):
    """layer_operation : layer_single constraints single_layer_op"""
    p[0] = {'command' : p[3], 'layer' : p[1], 'constraints' : p[2]}
def p_layer_op_single4(p):
    "layer_operation : single_layer_op constraints layer_single"
    p[0] = {'command' : p[1], 'layer' : p[3], 'constraints' : p[2]}
def p_layer_op_single5(p):
    """layer_operation : constraints single_layer_op layer_single"""
    p[0] = {'command' : p[2], 'layer' : p[3], 'constraints' : p[1]}
def p_layer_op_single6(p):
    """layer_operation : constraints layer_single  single_layer_op"""
    p[0] = {'command' : p[3], 'layer' : p[2], 'constraints' : p[1]}

    
######## two layers without any parameters
def p_two_layers_operations_easy1(p):
    ' layer_operation : layer_single layer_single two_op_easy'
    p[0]={'command' : p[3], 'layers' : [p[1],p[2]]}
def p_two_layers_operations_easy2(p):
    ' layer_operation : two_op_easy layer_single layer_single'
    p[0]={'command' : p[1], 'layers' : [p[2],p[3]]}
def p_two_layers_operations_easy3(p):
    ' layer_operation : layer_single  two_op_easy layer_single'
    p[0]={'command' : p[2], 'layers' : [p[1],p[3]]}

def p_two_op_easy(p):
    ''' two_op_easy :  AND
                                | COIN EDGE
                                | XOR
                                | NOT
                                | OR
                                | COINCIDENT EDGE
                                | NOT COIN EDGE
                                | NOT COINCIDENT EDGE    '''
    p[0]=' '.join(p[1:])
    
#####   two layers with several parameters    #####
def p_two_layer_sev_op(p):
    """two_layer_sev_op : CUT
                             | NOT CUT"""
    p[0] = ' '.join(p[1:])

def p_layer_operation_two_layer_sev1(p):
    """layer_operation : two_layer_sev_op layer_single layer_single several_ops"""
    p[0] = {'command' : p[1], 'layer1' : p[2], 'layer2' : p[3], 'options' : p[4]}

def p_layer_operation_two_layer_sev2(p):
    """layer_operation : layer_single two_layer_sev_op layer_single several_ops"""
    p[0] = {'command' : p[2], 'layer1' : p[1], 'layer2' : p[3], 'options' : p[4]}

def p_layer_operation_two_layer_sev3(p):
    """layer_operation : layer_single layer_single two_layer_sev_op several_ops"""
    p[0] = {'command' : p[3], 'layer1' : p[1], 'layer2' : p[2], 'options' : p[4]}

def p_several_options(p):
    """several_ops : several_ops constraints
                     | several_ops BY NET
                     | several_ops EVEN
                     | several_ops ODD
                     | empty"""
    if len(p) < 3:
        p[0] = []
    elif len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])
    elif len(p) == 4:
        p[0] = p[1]
        p[0].append(' '.join([p[2], p[3]]))

        

##########  connect ##########
def p_connect(p):
    ' connect_stmts : CONNECT connect_name connect_ops'
    p[0]= {'command' : 'CONNECT', 'layers': p[2], 'options' : p[3]}
    
def p_connect_by(p):
    ' connect_stmts : CONNECT connect_name BY name connect_ops'
    p[0]= { 'command' : 'CONNECT', 'layers' : p[2], 'by_layer' : p[4], 'options': p[5]}
      
def p_conn_name(p):
    '''connect_name : connect_name name
                        | name'''
    if len(p)==2:
        p[0]=[p[1]]
    else:
        p[0]=p[1]
        p[0].append(p[2])

def p_conn_ops(p):
    ''' connect_ops : empty
                        | DIRECT
                        | MASK
                        | DIRECT MASK'''
    if not p[1]:
        p[0]=[]
    else:
        p[0]=' '.join(p[1:]) 
        
######   attach  ######        
def p_attach(p):
    ' connect_stmts : ATTACH name name connect_ops'
    p[0]={'command': 'ATTACH', 'options' : p[4], 'layer' : p[3], 'text_layer' : p[2]}
        
#size
def p_layer_operation_size(p):
    """layer_operation : SIZE layer_single BY number size_options"""
    p[0] = {'command' : 'SIZE', 'layer' : p[2], 'value' : p[4], 'options' : p[5]}

def p_size_options_empty(p):
    """size_options : empty"""
    p[0] = []

def p_size_options2(p):
    """size_options : size_options OVERLAP ONLY
                    | size_options OVERUNDER
                    | size_options UNDEROVER"""
    p[0] = p[1]
    p[0].append({' '.join(p[2:]) : 1})

def p_size_options3(p):
    """size_options : size_options BEVEL number
                    | size_options STEP number
                    | size_options TRUNCATE number
                    | size_options MAXANGLE number"""
    p[0] = p[1]
    p[0].append({p[2] : p[3]})

def p_size_options4(p):
    """size_options : size_options INSIDE OF layer_single
                    | size_options OUTSIDE OF layer_single"""
    p[0] = p[1]
    p[0].append({' '.join(p[2:4]) : p[4]})


###################################
##########    measurements    ##########        
###################################


def p_measure_ops(p):
    ''' measure_ops : INT
                             | EXT
                             | ENC
                             | ENCLOSURE
                             | EXTERNAL
                             | INTERNAL'''
    p[0]=p[1]

def p_single_layer_measure(p):
    ' layer_operation : measure_ops layer_single constraints edge_mea_ops'
    p[0]={'command':p[1],'constraints': p[3], 'layer1':p[2],'options' :p[4]}
    
def p_double_layers_measure(p):
    ' layer_operation : measure_ops layer_single layer_single constraints edge_mea_ops'
    p[0]={'command':p[1], 'layer1':p[2], 'layer2':p[3], 'constraints': p[4], 'options' : p[5]}

    
def p_edge_mea_ops(p):
    ''' edge_mea_ops : empty
                                | edge_mea_ops metrics
                                | edge_mea_ops polygon_containment
                                | edge_mea_ops polygon_filter                        
                                | edge_mea_ops edge_shielding_filter                     
                                | edge_mea_ops connectivity_filter                           
                                | edge_mea_ops orientation_filter                        
                                | edge_mea_ops projection_filter                        
                                | edge_mea_ops angled_filter                        
                                | edge_mea_ops corner_filter                        
                                | edge_mea_ops intersection_filter                        
                                | edge_mea_ops reversals                        
                                | edge_mea_ops exclude_f
                                | edge_mea_ops region_output'''
    if len(p)<3:
        p[0]=[]
    else:
        p[0]=p[1]
        p[0].append(p[2])
        
def p_metrics_no_val(p):
    ''' metrics : OPPOSITE
                    | SQUARE
                    | OPPOSITE SYMMETRIC
                    | OPPOSITE FSYMMETRIC
                    | OPPOSITE1
                    | OPPOSITE2
                    | SQUARE ORTHOGONAL'''
    p[0]={ ' '.join(p[1:]) : 1}
def p_metrics_val(p):
    ''' metrics : OPPOSITE EXTENDED number
                    | OPPOSITE EXTENDED SYMMETRIC number
                    | OPPOSITE EXTENDED FSYMMETRIC number
                    | OPPOSITE EXTENDED1 number
                    | OPPOSITE EXTENDED2 number'''
    p[0]={ ' '.join(p[1:-1]) : p[len(p)-1]}


def p_polygon_containment(p):
    ''' polygon_containment : MEASURE ALL
                                        | MEASURE COIN
                                        | MEASURE COINCIDENT'''
    p[0]={ ' '.join(p[1:]) : 1}


def p_polygon_filter(p):
    ''' polygon_filter : NOTCH
                            | SPACE'''
    p[0]={ p[1] : 1}


def p_edge_shielding_filter(p):
    '''edge_shielding_filter : EXCLUDE SHIELDED esf_ops'''
    p[0]={'EXCLUDE SHIELDED' : 1}
    p[0].update(p[3])
    
def p_esf_ops_empty(p):
    ' esf_ops : empty'
    p[0]={}
def p_esf_ops(p):
    ''' esf_ops : esf_ops INTEGER
                    | esf_ops BY LAYER layer_single
                    | esf_ops COUNT INTEGER'''
    p[0]=p[1]
    if len(p)==3:
        p[0].update({ 'level' : p[2]})
    elif len(p)==4:
        p[0].update({ 'COUNT' : p[3]})
    elif len(p)==5:
        p[0].update( { 'BY LAYER' : p[4]})       
    
    
def p_connectivity_filter(p):
    ''' connectivity_filter : CONNECTED
                                | NOT CONNECTED'''
    p[0]= { ' '.join(p[1:]) : 1}
        
        
def p_orientation_filter(p):     
    ''' orientation_filter : ACUTE ALSO
                                 | ACUTE ONLY
                                 | NOT ACUTE
                                 | PARALLEL ALSO
                                 | PARALLEL ONLY
                                 | NOT PARALLEL
                                 | PARA ALSO
                                 | PARA ONLY
                                 | NOT PARA
                                 | NOT PERPENDICULAR
                                 | NOT PERP
                                 | PERP ONLY
                                 | PERPENDICULAR ONLY
                                 | PERP ALSO
                                 | PERPENDICULAR ALSO
                                 | NOT OBTUSE
                                 | OBTUSE ONLY
                                 | OBTUSE ALSO'''
    p[0]={' '.join(p[1:]) : 1}


def p_projection_filter1(p):
    ''' projection_filter : PROJECTING
                                | PROJ
                                | NOT PROJECTING
                                | NOT PROJ'''
    p[0]={' '.join(p[1]) : 1}
def p_projection_filter2(p):
    ''' projection_filter : PROJ constraints
                                | PROJECTING constraints'''
    p[0]={ p[1] :1 , 'length' : p[2]}

def p_angled_filter(p):
    ''' angled_filter : ANGLED
                            | ANGLED constraints'''
    if len(p)==2:
        p[0]={'ANGLED' : 1}
    elif len(p)==3:
        p[0]= {'ANGLED' :1 , 'angle_constraint' : p[2]}

def p_corner_filter(p):
    ''' corner_filter : CORNER
                            | NOT CORNER
                            | CORNER TO EDGE
                            | CORNER TO CORNER
                            | CORNER TO CORNER constraints'''
    if len(p)<5:
        p[0]={ ' '.join(p[1:]) : 1}
    elif len(p)==5:
        p[0]={'CORNER TO CORNER' : 1, 'corner_constraint' : p[4]}

def p_intersection_filter(p):
    ''' intersection_filter : inter_ops
                                    | inter_only'''
    p[0]=p[1]

def p_inter_ops(p):
    ''' inter_ops : ABUT
                        | OVERLAP
                        | SINGULAR
                        | ABUT constraint'''
    if len(p)==2:
        p[0]={ p[1] : 1}
    elif len(p)==3:
        p[0]={ p[1] : 1, 'abut_constraint' : p[2]}
        
def p_inter_only(p):
    ' inter_only : inter_ops INTERSECTING ONLY'
    p[0]=p[1]
    p[0].update({ 'INTERSECTING ONLY' : 1})
        
def p_reversals(p):
    ''' reversals : INSIDE ALSO
                        | OUTSIDE ALSO'''
    p[0]={ ' '.join(p[1]) : 1}
        
def p_exclude_f(p):
    ' exclude_f : EXCLUDE FALSE'
    p[0]={'EXCLUDE FALSE' : 1}
    
def p_region_output(p):
    ''' region_output : REGION
                            | REGION EXTENTS
                            | REGION CENTERLINE
                            | REGION CENTERLINE number'''
    if len(p)==2:
        p[0]={ 'REGION' : 1}
    elif len(p)==3:
        p[0]={'REGION' :p[2]}
    elif len(p)==4:
        p[0]={p[1]:p[2], 'line_width':p[3]}

        
        
        
#######################################################
###############                DFM Property                 ##############
#######################################################
def p_dfm_property(p):
    'layer_operation : DFM PROPERTY name names dfmp_options pro_defs'
    p[0]= {'command' : 'DFM PROPERTY', 'primary_layer': p[3], 
           'secondary_layers' : p[4], 'options': p[5], 'properties' : p[6]}

def p_dfmp_options_specific(p):
    '''dfmp_options :  dfmp_options dfmp_split
                            | dfmp_options dfmp_inside
                            | dfmp_options dfmp_bycell
                            | dfmp_options dfmp_bynet
                            | dfmp_options dfmp_interact'''
    p[0]=p[1]
    p[0].update(p[2])
   
def p_dfmp_interact(p):
    ''' dfmp_interact : INTERSECTING
                            | OVERLAP interact_ops
                            | NODAL interact_ops'''
    if len(p)==2:
        p[0]= {'interact': p[1]} 
    else:
        aa={p[1] : 1}
        aa.update(p[2])
        p[0]= {'interact': aa} 

def p_interactop_empty(p):
    'interact_ops : empty'
    p[0]={ }        
    
def p_interact_ops(p):
    ''' interact_ops : interact_ops ABUT ALSO
                            | interact_ops ABUT ALSO SINGULAR
                            | interact_ops MULTI
                            | interact_ops NOMULTI
                            | interact_ops NOPUSH
                            | interact_ops REGION'''
    p[0]=p[1]
    p[0].update({''.join(p[2:]):1})
                  
def p_dfmp_bycell(p):
    'dfmp_bycell : BY CELL netcellops'
    p[0]= {'BY CELL' : p[3]}
    
def p_netcellops_empty(p):
    'netcellops : empty'
    p[0]={ }

def p_netcellops(p):
    '''netcellops : ONLY
                        | NOHIER
                        | NOPSEUDO'''
    p[0]={''.join(p[1]) : 1}
    
def p_dfmp_bynet(p):
    ''' dfmp_bynet : netops BY NET netcellops
                        | BY NET netcellops'''
    if len(p)==4:
        p[0]={'BY NET' : p[3]}
    elif len(p)==5:
        p[4].update(p[1])
        p[0]= {'BY NET' : p[4]}   
    
def p_netops(p):
    '''netops : ACCUMULATE
                    | ACCUMULATE ONLY
                    '''
    if len(p)==2:
        p[0]={'ACCUMULATE' : 1}
    elif len(p)==3:
        p[0]={'ACCUMULATE ONLY' : 1}

def p_dfmp_inside(p):
    'dfmp_inside : INSIDE OF coord coord coord coord'
    t1=tuple(p[3:5])
    t2=tuple(p[5:7])
    p[0]={'INSIDE OF' : [t1,t2] }

def p_dfmp_split(p):
    ''' dfmp_split : SPLIT
                        | SPLIT ALL
                        | SPLIT PRIMARY '''
    p[0]={ ' '.join(p[1:]) : 1}

def p_dfmp_options_simple(p):
    '''dfmp_options : dfmp_options CORNER
                            | dfmp_options GLOBALXY
                            | dfmp_options CONNECTED
                            | dfmp_options NOT CONNECTED'''
    p[0]=p[1]
    p[0].update( {' '.join(p[2:]) : 1})
    
def p_dfmp_options_empty(p):
    'dfmp_options : empty'
    p[0]={ }

def p_pro_defs_empty(p):
    ' pro_defs : empty'
    p[0] = [ ]
    
def p_pro_definition(p):
    ' pro_defs : pro_defs pro_def'
    p[0]=p[1]
    p[0].append(p[2])
    
def p_pro_def(p):
    'pro_def : LBRACKET pro_name ASSIGN expr RBRACKET alter_constraints '
    p[0]= { 'property' : p[2], 'expr' :  p[4], 'alter_constraints' : p[6] }

def p_pro_name(p):
    ''' pro_name : MINUS
                        | name 
                        | PLUS name'''
    p[0]=' '.join(p[1:])
def p_alter_constraints(p):
    '''alter_constraints : constraints
                                |  NEGATION constraints'''
    if len(p)==2:
        p[0]={'constraints' : p[1]}
    elif len(p)==3:
        p[0]={'constraints': p[2], 'NEGATION': 1}

def p_alter_constraints_empty(p):
    'alter_constraints : empty'
    p[0]=[]



##################################################
###############           net area ratio             #############
##################################################
def p_net_area_ratio_std(p):
    ' layer_operation : NET AREA RATIO nar_layers expr_op constraints nar_options'
    p[0]= {'command' : 'NET AREA RATIO', 'layers': p[4], 'expr' : p[5], 'constraints' : p[6], 'options' : p[7]}
def p_net_area_ratio_single(p):
    ' layer_operation : NET AREA RATIO nar_layer LBRACKET expr RBRACKET constraints nar_options'
    p[0]={'command': 'NET AREA RATIO', 'layer': p[4], 'expr': p[6], 'constraints': p[8], 'options': p[9]}
    
def p_net_area_ratio_stdover(p):
    ' layer_operation : NET AREA RATIO nar_layers OVER nar_layers expr_op constraints nar_options'
    p[0]={'command' : 'NET AREA RATIO', 'layers': p[4], 'd_layers': p[6], 'expr' : p[7], 'constraints' : p[8], 'options' : p[9]}    # OVER only once ,so not in recursion

def p_expr_op_empty(p):
    ' expr_op : empty'
    
def p_expr_op(p):
    ' expr_op : LBRACKET expr RBRACKET'
    p[0]= p[2]
    
def p_nar_layers(p):
    '''nar_layers : nar_layers nar_layer
                        | nar_layer'''
    if len(p)==2:
        p[0]=[p[1]]
    elif len(p)==3:
        p[0]=p[1]
        p[0].append(p[2])
        
def p_nar_layer(p):
    ' nar_layer : name nar_layer_op'
    p[0]= {'layer': p[1], 'option': p[2]}
    
def p_nar_layer_op_empty(p):
    ' nar_layer_op : empty'
    p[0]=[]

def p_nar_layer_op(p):
    ''' nar_layer_op : nar_scale
                            | nar_only
                            | nar_scale nar_only
                            | nar_only nar_scale'''
    if len(p)==2:
        p[0]=p[1]
    elif len(p)==3:
        p[0]=p[1]
        p[0].update(p[2])
    
def p_nar_scale(p):
    ' nar_scale : SCALE BY number'
    p[0]={'SCALE BY' : p[3]}
    
def p_nar_only(p):
    ''' nar_only : COUNT ONLY
                    | PERIMETER ONLY'''
    p[0]={' '.join(p[1:]) : 1}
    
def p_nar_options_empty(p):
    ' nar_options : empty'
    p[0]=[]
    
def p_nar_options(p):
    '''nar_options : nar_options nar_accu
                         | nar_options nar_inside
                         | nar_options nar_rdb
                         '''             
    p[0]=p[1]
    p[0].append(p[2])
    
def p_nar_accu(p):
    ' nar_accu : ACCUMULATE nar_alayers'
    p[0]={'ACCUMULATE' : p[2]}
    
def p_nar_alayers_emp(p):
    ' nar_alayers : empty'
    p[0]=[]
def p_nar_alayer(p):
    ' nar_alayers : name names'
    p[0]=p[2].insert(0,p[1])
        
def p_nar_options_inside(p):
    '''nar_inside : INSIDE OF LAYER name
                        | INSIDE OF LAYER name BY NET'''
    if len(p)==5:
        p[0]={'INSIDE OF LAYER' : p[4]}
    else:
        p[0]={'INSIDE OF LAYER' : p[4], 'BY NET' : 1}
        
def p_nar_rdb_part(p):
    'nar_rdb : rdb_only name rdb_ops'
    p[0]={p[1]:p[2], 'options':p[3]}

def p_rdb_only(p):
    ''' rdb_only : RDB
                    | RDB ONLY'''
    p[0]=' '.join(p[1:])

def p_nar_rdb_ops_spec(p):
    ''' rdb_ops :  rdb_ops mags
                    |  rdb_ops bylay 
                    |  rdb_ops rdb_layers
                    |  empty '''
    if len(p)<3:
        p[0]=[]
    else:
        p[0]=p[1]
        p[0].append(p[2])
  
def p_mags(p):
    ' mags : MAG number'
    p[0]={'MAG' : p[2]}

def p_bylay(p):
    'bylay : BY LAYER'
    p[0]= 'BY LAYER' 

def p_rdb_layers1(p):
    ''' rdb_layers : name_max
                        | rdb_layers name_max'''
    if len(p)==2:
        p[0]={'rdb_layers' :p[1]}
    elif len(p)==3:
        res=p[1].get('rdb_layers')
        res1=[res,p[2]]
        p[0]={'rdb_layers' : res1}
           
def p_name_max(p):
    ''' name_max : name
                        | name MAXIMUM INTEGER'''
    if len(p)==2:
        p[0]={p[1]: []}
    else:
        kk=['MAXIMUM']
        kk.append(p[3])
        p[0]={p[1]: kk}


#####   DFM FUNCTION   #####
def p_dfm_function(p):
    ''' element : DFM FUNCTION LBRACKET name LPAREN dfm_args RPAREN RBRACKET'''
    p[0]={'command' : 'DFM FUNCTION', 'func_name': p[4],'args': p[6]}

def p_dfm_args(p):
    ''' dfm_args : dfm_arg
                        | dfm_args COMMA dfm_arg'''
    if len(p)==2:
        p[0]=p[1]
    else:
        p[0]=p[1]
        p[0].update(p[3])

def p_dfm_arg_basic(p):
    ''' dfm_arg : NUMBER name
                    | LAYER name
                    | STRING name'''
    p[0]={'type': p[1], 'argument':p[2]}
    
    
    
    

# number
# here we define only positive number, negative to be solved
def p_number(p):
    ''' number : expr'''  #somewhere the number can be an expr
    p[0]=p[1]

# coord - coordinate, can be negative
def p_coord(p):
    ''' coord : FLOAT
                | INTEGER
                | LPAREN MINUS FLOAT RPAREN
                | LPAREN MINUS INTEGER RPAREN'''
    if len(p)==2:
        p[0]=p[1]
    else:
        p[0]=-p[3]

#expr (used in DFM property, net area ratio,...)
def p_expr_num(p):
     ''' expr : INTEGER
                | FLOAT'''
     p[0] = p[1]   
    
def p_expr_name(p):
    'expr : name'
    p[0]={'variable' : p[1]}
def p_expr_group(p):
    """expr : LPAREN expr RPAREN"""
    p[0] = p[2]
    
def p_expr_biops(p):
    ''' expr : expr PLUS expr
                | expr MINUS expr
                | expr TIMES expr
                | expr DIVIDE expr
                | expr POW expr
                | expr MODULUS expr'''
    p[0]={'binary_op': p[2], 'left' : p[1], 'right' : p[3]}

def p_expr_uniops(p):
    ''' expr : MINUS expr %prec UMINUS
                | NEGATION expr
                | COMPLEMENT expr'''
    p[0]={'unary_op': p[1], 'expr' : p[2]}
    
def p_expr_funcs(p):
    ''' expr : functions'''
    p[0]=p[1]

def p_functions_stmt(p):
    ''' functions : funcs LPAREN args RPAREN
                        | name LPAREN args RPAREN'''
    p[0]= {'args': p[3], 'call_func': p[1]}    

def p_funcs_builtin(p):
    ''' funcs : AREA
                 | COUNT
                 | PERIMETER
                 | SIN
                 | COS
                 | TAN
                 | MAX
                 | MIN
                 | SQRT
                 | EXP
                 | LOG'''
    p[0]=p[1]

def p_func_args_em(p):
    ' args : empty'
    p[0]=[]
def p_func_args_1(p):
    ' args : expr '
    p[0]=[p[1]]
def p_func_args_x(p):
    'args : args COMMA expr'
    p[0]=p[1]
    p[0].append(p[3])

def p_expr_condition(p):
    ' expr : expr QMARK expr COLONS expr'
    p[0]={'condition':p[1], 'result_true':p[3], 'result_false':p[5]}


# constraints
def p_constraints(p):
    ''' constraints : constraint constraint
                        |  constraint'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1],p[2]]
        
def p_compare(p):
    ''' compare : EQ 
                      | NE
                      | GT 
                      | LT
                      | GE 
                      | LE  '''
    p[0]=p[1]
    
def p_constraint(p):
    ' constraint : compare number'
    p[0]= {'op' : p[1], 'value' : p[2]}

#name(sometimes used as variable)
def p_names(p):
    ''' names : names name
                    | empty'''
    if len(p)<3:
        p[0]=[]
    elif len(p)==3:
        p[0]=p[1]
        p[0].append(p[2])

def p_name(p):
    ''' name : ID
                  | STRINGS'''
    p[0]=p[1]



def p_empty(p):
    'empty :  '
    pass   #!!!


parser=yacc.yacc()
'''    
if __name__ == '__main__':
    if len(sys.argv)==3:
        da=open(sys.argv[1]).read()
        p = parser.parse(da)
        d = yaml.safe_dump(top.gen)
        f = open(sys.argv[2], 'w')
        f.write(d)
        f.close()
        sys.exit(0)

dd=input(' ')
pp=parser.parse(dd)
daa=yaml.safe_dump(top.gen)
print(daa)
print(pp)
f1=open('f1','w')
f1.write(daa)
f1.close()

f2=open('f2','w')
f2.write(pp)
f2.close()
  
'''  