import svn.remote

'''
目的：得到版本之间修改和增加的文件，不包括目录
输入参数：源码的SVN地址，
 source_file_list=[{'path': 'https://xxx/xxx.java','item': 'modified','kind': 'file'},
  {'path': 'https://xxx/xxx.gif','item': 'added','kind': 'file'}]  
'''

def  diff_summary_files(svn_source_dir,start_version,end_version):
    l = svn.remote.RemoteClient(svn_source_dir)
    source_file_list = l.diff_summary(start_version,end_version)   
    #转换成编译后的路径,只增加修改和删除的路径,不包括目录
    source_files = [f.get('path') for f in source_file_list if f.get('item')=='modified' or f.get('item')=='added' and f.get('kind')=='file']
    return source_files