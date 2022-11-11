import random
import time
def partition(lis,l,r):
    tmp=lis[l]
    while l<r:
       while l<r and lis[r]<=tmp:
           r-=1
       lis[l]=lis[r]
       while l<r and lis[l]>=tmp:
           l+=1
       lis[r]=lis[l]
    lis[l]=tmp
    return l

def quick_sort(lis,l,r):
  if l<r: 
      q=partition(lis,l,r) 
      quick_sort(lis,l,q-1) 
      quick_sort(lis,q+1,r)
t1=time.time()
lis=list(range(200))
random.shuffle(lis)
print(lis)
quick_sort(lis,0,len(lis)-1)
print(lis)
t2=time.time()
print(t2-t1)
