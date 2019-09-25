#!/usr/bin/env python
# coding=utf-8
import subprocess
import paramiko

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