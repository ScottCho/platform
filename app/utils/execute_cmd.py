#!/usr/bin/env python
# coding=utf-8
import subprocess
import paramiko

from  app import socketio

#传入命令和交互的内容，execute_cmd('python','print("hello")')
def execute_cmd(cmd,*content):
    p = subprocess.Popen(cmd,shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    if content:
        stdout,stderr =  p.communicate(bytes(content[0], encoding="utf8"))
    else:
        stdout,stderr =  p.communicate()
    if p.returncode != 0:
        return p.returncode, stderr
    return p.returncode, stdout



# 执行的结果通过socket-io发送到前端
@socketio.on('event2',namespace='/task')
def socket_shell(cmd):
    p = subprocess.Popen(cmd,shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    while True: 
        line = p.stdout.readline().strip()
        line=line.decode(encoding='utf-8')
        print('line='+line)
        socketio.emit('event2', line,namespace='/task')
        if not line:
            break

    

        
           


#利用paramiko调用ssh在远程机器执行命令
def remote_execute_command(hostname,command,port=22,username=None,password=None):
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname,username=username,port=port,password=password)
        stdin,stdout,stderr = client.exec_command(command)
        err = stderr.readlines()
        if err:
            return err
        else:
            return(stdout.readlines())



# 远程执行的结果通过socket-io发送到前端
@socketio.on('event2',namespace='/task')
def remote_socket_shell(command='ping -c3 www.qq.com',hostname='127.0.0.1',username='root',password='123456',port=22):
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname,username=username,port=port,password=password)
        stdin,stdout,stderr = client.exec_command(command)
        while True:
            message = stdout.readline().strip()
            err = stderr.readline().strip()
            line = ''
            if err:
                line=err
            else:
                line=message
            socketio.emit('event2', line,namespace='/task')
            if not line:
                break   
