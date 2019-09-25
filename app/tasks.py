#!/usr/bin/python
#-*- coding: UTF-8 -*-
import shutil
import os
from . import celery

from app.utils.execute_cmd import remote_execute_command

#执行远程命令
@celery.task()
def  remote_shell(host,command,username,password):
    out=remote_execute_command(host,command,username=username,password=password)
    return(out)