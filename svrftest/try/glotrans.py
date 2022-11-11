from decimal import Decimal
import yaml,time,sys
from collections import defaultdict
from mini import *
# Graph, with topological sort 
class Graph: 
    def __init__(self,vertices): 
        self.graph = defaultdict(list) 
        self.V = vertices
  
    def addEdge(self,u,v): 
        ii=self.V.index(u)
        self.graph[ii].append(v) 
  
    def topologicalSortUtil(self,v,visited,stack): 
        vv=self.V.index(v)
        visited[vv] = True
  
        for i in self.graph[vv]: 
            if visited[self.V.index(i)] == False: 
                self.topologicalSortUtil(i,visited,stack) 
  
        stack.insert(0,v) 
        
  
    def topologicalSort(self): 
        visited = [False]*len(self.V) 
        stack =[] 
  
        for i in range(len(self.V)): 
            if visited[i] == False: 
                self.topologicalSortUtil(self.V[i],visited,stack)
        
        stack.reverse() 
  
        return stack
    def findnodes(self, u):
        visited=[False]*len(self.V)
        stack=[]
        self.topologicalSortUtil(u,visited,stack)
        return stack

#with open('ji','r') as file:
#    a1=yaml.safe_load(file)


def sortsvtf(a1):
        
    def varincomment(op):
        lis=[]
        la=[]
        for i in range(1,len(op)):
            if op[i]=='^' and op[i-1]!='\\':
                ll=''
                for j in range(i+1,len(op)):
                    if op[j] not in [' ','\\','^']:
                        ll+=op[j]
                    else:
                        break
                lis.append({ll:i})
        for h in range(len(lis)):
            la+=list(lis[h]) 
        return la
    def commconvert(op,d0):
        b1=[]
        for i in range(1,len(op)):
            if op[i]=='^' and op[i-1]!='\\':
                ll=''
                for j in range(i+1,len(op)):
                    if op[j] not in [' ','\\','^']:
                        ll+=op[j]
                    else:
                        break
                b1.append({ll:i})  
        pl=[]
        ele=[]
        for i in b1:
            pl+=list(i.values())
            ele+=list(i.keys())
        pl.append(len(op))
        op0=''+op[:pl[0]]
        for j in range(len(pl)-1):
            opc=op[pl[j]:pl[j+1]]
            for k in range(len(d0)):
                if d0[k].get('out1') and d0[k]['out1']==ele[j]:
                    ok=d0[k]['value'][0]
            op1=opc[len(ele[j])+1:]
            op2=str(ok)+op1
            op0+=op2
        #print(op0[1:])
        return op0[1:]


    def get_dic(dic,t_key ,res=[]):
        if isinstance(dic, dict):
            for key in dic.keys():
                data=dic[key]
                get_dic(data,t_key,res=res)
                if key==t_key:
                    res.append(data)
                #print(res)
        elif isinstance(dic,list):
            for data in dic:
                get_dic(data,t_key,res=res)
        return res

    def inout(aa):
        for i in range(len(aa)):
            if aa[i].get('command'):
                if aa[i]['command']=='LAYER':
                    aa[i]['out']=aa[i]['name']
                    #del aa[i]['name']
                    aa[i]['in']=aa[i]['layers']
                    #del aa[i]['layers']
                elif aa[i]['command'] in two_ops:
                    aa[i]['out']=aa[i]['result']
                    aa[i]['in']=aa[i]['layers']
                    #del aa[i]['result']
                    #del aa[i]['layers']
                elif aa[i]['command'] in one_op:
                    aa[i]['out']=aa[i]['result']
                    aa[i]['in']=[aa[i]['layer']]
                    if aa[i].get('constraints'):
                        avar=[]
                        for kk in range(len(aa[i]['constraints'])):
                            abb=aa[i]['constraints'][kk]
                            ac=get_dic(abb,'variable')
                            avar+=ac
                        avar=list(set(avar))
                        aa[i]['in1']=avar          
                    #del aa[i]['result']
                    #del aa[i]['layer']
                elif aa[i]['command'] in mea_op:
                    aa[i]['out']=aa[i]['result']
                    #del aa[i]['result']
                    s1=aa[i]['layer1']
                    ss=[s1]
                    if aa[i].get('layer2'):
                        s2=aa[i]['layer2']
                        ss.append(s2)
                        del aa[i]['layer2']
                    aa[i]['in']=ss
                    #del aa[i]['layer1']
        return(aa)

    def blocksort(b):
        inn=[]
        out=[]
        a=inout(b['block'])
        in1=[]
        for i in range(len(a)):
            if a[i].get('command')!='RULECOMMENT':
                for l1 in range(len(a[i]['in'])):
                    inn.append(a[i]['in'][l1])
                out.append(a[i]['out'])
            else:
                op=a[i]['content']
                in1=varincomment(op)
                a[i]['content']=commconvert(op,a1)
        share=[]
        for k in inn:
            if k in out:
                share.append(k)
        #print(inn)

        in0=[l for l in inn if l not in share]        
        g=Graph(a)
        for i in range(len(a)):
            if a[i].get('out'):
                ou=a[i]['out']
                for j in range(len(a)):
                    if a[j].get('in') and ou in a[j]['in']:
                        g.addEdge(a[j],a[i])
        d=g.topologicalSort()
        b['block']=d
        b['in']=in0
        b['in1']=list(set(in1))
        #print(in1,b)
        return b
    def varconvert(var):
        for j1 in range(len(var)):
            if var[j1].get('in1'):
                oj=var[j1]['value'][0]
                if type(oj)==dict:
                    v=varexpr(oj,var)
                    var[j1]['value'][0]=v
                    
        return var

    def varexpr(oj,var):
        if oj.get('binary_op'):
            sign=oj.get('binary_op')
            aa1=oj['left']
            aa2=oj['right']
            if type(aa1)==dict:
                if aa1.get('variable'):
                    aa0=aa1['variable']
                    for k1 in range(len(var)):
                        if var[k1]['out1']==aa0:
                            aa1=var[k1]['value'][0]
                else:
                    aa1=varexpr(aa1,var)
            if type(aa2)==dict:
                if aa2.get('variable'):
                    aa0=aa2['variable']
                    for k1 in range(len(var)):
                        if var[k1]['out1']==aa0:
                            aa2=var[k1]['value'][0]
                else:
                    aa2=varexpr(aa2,var)            
            if sign == '+':
                v=Decimal(str(aa1))+Decimal(str(aa2))
            elif sign == '-':
                v=Decimal(str(aa1))-Decimal(str(aa2))
            elif sign=='*':
                v=Decimal(str(aa1))*Decimal(str(aa2))
            elif sign=='/':
                v=Decimal(str(aa1))/Decimal(str(aa2))
            return float(str(v))
        elif oj.get('expr'):
            ve=oj.get('expr')
            v1=v_unary(ve,var)[0]
            v2=v_unary(ve,var)[1]
            if v2%2==0:
                return -v1
            else:
                return v1

    def v_unary(ve,var):
        p=0
        if ve.get('variable'):
            vv=ve['variable']
            for k1 in range(len(var)):
                if var[k1]['out1']==vv:
                    ve=var[k1]['value'][0]                
        elif ve.get('binary_op'):
            ve=varexpr(ve,var)
        elif ve.get('expr'):
            ve=v_unary(ve.get('expr'),var)[0]
            p+=1
        return [ve,p]

                

    
    two_ops=['XOR','AND','OR','NOT','COIN EDGE']    
    one_op=['SIZE', 'ANGLE','AREA']
    mea_op=['ENC','EXT','INT']
    drc_inc=False
    var1=[]
    for i0 in range(len(a1)):
        if a1[i0].get('command'):
            if a1[i0]['command']=='RULE':
                a1[i0]=blocksort(a1[i0])
            elif a1[i0]['command']=='CONNECT':
                in1=a1[i0].get('layers')
                if a1[i0].get('by_layer'):
                    in2=a1[i0].get('by_layer')
                    in1.append(in2)
                    #del a1[i0]['by_layer']
                #del a1[i0]['layers']
                a1[i0].update({'in': in1})
                
            elif a1[i0]['command']=='VARIABLE':
                cd=get_dic(a1[i0]['value'],'variable',[])
                if cd!=[]:
                    a1[i0].update({'in1':cd})
                var1.append(a1[i0])
            else: 
                a1[i0]=inout([a1[i0]])[0]
        if a1[i0].get('config') == 'DRC INCREMENTAL CONNECT':
            if a1[i0]['switch']=='YES':
                drc_inc=True
                
    a11=[t for t in a1 if t not in var1]
    var1=varconvert(var1)
    a1=a11+var1
    
    g=Graph(a1)
    for i in range(len(a1)):
        if a1[i].get('out'):
            ou=a1[i].get('out')
            for j in range(len(a1)):
                if a1[j].get('in') and ou in a1[j].get('in'):
                    g.addEdge(a1[j],a1[i])
        if a1[i].get('out1'):
            ou1=a1[i].get('out1')
            for j in range(len(a1)):
                if a1[j].get('in1') and ou1 in a1[j].get('in1'):
                    g.addEdge(a1[j],a1[i])
    a1=g.topologicalSort()

    if not drc_inc:
        conn=[]
        acon=[]
        co1=[]
        for i in range(len(a1)):
            if a1[i].get('command')=='CONNECT':
                for j in a1[i]['in']:
                    conn.append(j)
                acon.append(a1[i])
        conn=list(set(conn))
        #print(conn)
        for i in range(len(a1)):
            if a1[i].get('out') in conn:
                for l in g.findnodes(a1[i]):
                    if l not in co1:
                        co1.append(l)
        #print(co1)
        g1=Graph(co1)
        for i in range(len(co1)):
            if co1[i].get('out'):
                ou=co1[i].get('out')
                for j in range(len(co1)):
                    if co1[j].get('in') and ou in co1[j].get('in'):
                        g1.addEdge(co1[j],co1[i])
            if co1[i].get('out1'):
                ou1=co1[i].get('out1')
                for j in range(len(co1)):
                    if co1[j].get('in1') and ou1 in co1[j].get('in1'):
                        g1.addEdge(co1[j],co1[i])
        c1=g1.topologicalSort()

        co2=[l for l in a1 if l not in co1+acon]
        g2=Graph(co2)
        for i in range(len(co2)):
            if co2[i].get('out'):
                ou=co2[i].get('out')
                for j in range(len(co2)):
                    if co2[j].get('in') and ou in co2[j].get('in'):
                        g2.addEdge(co2[j],co2[i])
            if co2[i].get('out1'):
                ou1=co2[i].get('out1')
                for j in range(len(co2)):
                    if co2[j].get('in1') and ou1 in co2[j].get('in1'):
                        g2.addEdge(co2[j],co2[i])
        c2=g2.topologicalSort()
        a0=c1+acon+c2
        #with open('tt','w') as f:
        #    f.write(yaml.safe_dump(a0))
            
    else:
        g0=Graph(a1)
        for j in range(len(a1)):
            if a1[j].get('out'):
                oo=a1[j].get('out')
                for k in range(len(a1)):
                    if a1[k].get('in') and oo in a1[k].get('in'):
                        g0.addEdge(a1[k],a1[j])
        cc0=g0.topologicalSort()
        a0=cc0

                    
    def simplify(li,var):
        lli=[0]*len(li)
        for i in range(len(li)):
            if li[i].get('command'):
                if li[i]['command']=='LAYER':
                    lli[i]=[ li[i]['out'],'LAYER', li[i]['in']]
                elif li[i]['command'] in two_ops:
                    lli[i]=[li[i]['out'],li[i]['command'],li[i]['in']]
                elif li[i]['command'] in mea_op:
                    lli[i]=[li[i]['out'], li[i]['command'], li[i]['in']]
                elif li[i]['command'] in one_op:
                    cc=li[i]['constraints']
                    for c in range(len(cc)):
                        k=cc[c]['value']
                        print(k)
                        if type(k)==dict:
                            if not k.get('variable'):
                                kk=varexpr(k,var)
                                cc[c]['value']=kk
                            else:
                                #c0=0
                                for vi in range(len(var)):
                                    if var[vi]['out1']==k['variable']:
                                        c0=var[vi]['value'][0]
                                cc[c]['value']=c0
                                
                                                
                    lli[i]=[li[i]['out'],li[i]['command'],li[i]['in'],li[i]['constraints']]
                    if li[i].get('in1'):
                        lli[i].append(li[i]['in1'])
                elif li[i]['command']=='RULE':
                    li[i]['block']=simplify(li[i]['block'],var)
                    lli[i]=[li[i]['name'],li[i]['in'],li[i]['block'],li[i]['results']]
                    if li[i].get('in1'):
                        lli[i].append(li[i]['in1'])
                elif li[i]['command']=='VARIABLE':
                    lli[i]=[li[i]['out1'],'VARIABLE',li[i]['value']]
                    if li[i].get('in1'):
                        lli[i].append(li[i]['in1'])
                elif li[i]['command']=='CONNECT':
                    lli[i]=[li[i]['command']]
                    if li[i].get('by_layer'):
                        u=li[i]['by_layer']
                        u1=[y for y in li[i]['in'] if y not in u]
                        lli[i].append(u1)
                        lli[i].append({'by_layer':li[i]['by_layer']})
                    else:
                        lli[i].append(li[i]['in'])
                else: 
                    lli[i]=[li[i]]
            else:
                lli[i]=[li[i]]
        
        #print(lli)
        return lli
    lo=simplify(a0,var1)
    return lo
    #lo=simplify(a0,var1)

'''
with open('fuc','w') as f:
    lo=[str(lo1)+'\n' for lo1 in lo]
    f.writelines(lo)
'''
if __name__ == '__main__':
    
    if len(sys.argv)==3:
        t1=time.time()
        da=open(sys.argv[1]).read()
        p = parser.parse(da)
        #d = yaml.safe_dump(top.gen)
        #ee=yaml.safe_load(d)
        f = open(sys.argv[2], 'w')
        ee=top.gen
        ll=sortsvtf(ee)
        l0=[str(lo1)+'\n' for lo1 in ll]
        f.writelines(l0)
        f.close()
        t2=time.time()
        print(t2-t1)
        sys.exit(0)
    







