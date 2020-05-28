'''
@Author: your name
@Date: 2020-04-21 13:53:15
@LastEditTime: 2020-04-21 13:53:16
@LastEditors: your name
@Description: In User Settings Edit
@FilePath: /platform/test.py
'''

# import subprocess

# p = subprocess.Popen("sqlplus wluser/demo123@192.168.0.21:1521/winglungsit @/update/WINGLUNG/2799/DB/WLUSER_20200511_01_ALL.sql",shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# while True:
#     line = p.stdout.readline()
#     line = line.decode(encoding='utf-8')
#     if  line:
#         print(line)
#     else:
#         break

# def socket_shell(cmd):
#     p = subprocess.Popen(cmd,
#                          shell=True,
#                          stdin=subprocess.PIPE,
#                          stdout=subprocess.PIPE,
#                          stderr=subprocess.STDOUT)
#     while True:
#         line = p.stdout.readline().strip()
#         line = line.decode(encoding='utf-8')
#         print('line=' + line)
#         if not line:
#             break


with open('/tmp/frog.log', 'a') as f:
    f.write('test')