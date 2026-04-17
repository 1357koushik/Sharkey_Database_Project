class Bruteforceindex:
  def __init__(self):
    self.data=[]
  def insert(self,key,value):
    found,a=self.search(key)
    if found:
      self.update(key,value)
    else:
      self.data.append((key,value))
  def search(self,key):
    for k,v in self.data:
      if k==key:
        return (True,v)
    return (False,None)
  def delete(self,key):
    for i,(k,v) in enumerate(self.data):
      if k==key:
        self.data.pop(i)
        return True
    return False
  def update(self,key,newval):
    for i,(k,v) in enumerate(self.data):
      if k==key:
        self.data[i]=(k,newval)
        return True
    return False
  def getall(self):
    return self.data.copy()
  def range_query(self,st,end):
    return [i for i in self.data if st<=i[0]<=end]
