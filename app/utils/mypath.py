import os
import shutil



def dir_remake(path):
    '''
    创建目录，如果存在则删除重建
    '''
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
