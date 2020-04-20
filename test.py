'''
@Author: your name
@Date: 2020-04-20 11:18:20
@LastEditTime: 2020-04-20 11:34:21
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /platform/test.py
'''
class A():
   
   def __init__(self,name,score):
      self.name = name
      self.score = score
      self.package = self.score+'_'+self.name
   
   # @property
   # def package(self):
   #      return self.score+'_'+self.name

   # @package.setter
   # def package(self):
   #    self.package = self.score+'_'+self.name



s = A('张三','59')
s.score = '60'
print(s.package)


   
   