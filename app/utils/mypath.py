import os
import shutil


# 判断目录是否存在，存在则删除重建
def dir_remake(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
