import time
s=0
def hh(n,a,b,c):
  global s
  if n>0:
      hh(n-1,a,c,b)
      print("from %s to %s"% (a,c))
      hh(n-1,b,a,c)
      s+=1  
k=int(input("tower="))
t1=time.time()
print(hh(k,'a','b','c'))
t2=time.time()
print(s)
print(t2-t1)
