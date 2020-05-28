'''
@Author: your name
@Date: 2020-04-24 11:37:22
@LastEditTime: 2020-04-24 15:24:43
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /platform/app/utils/jenkins.py
'''
import requests
import os

from jenkinsapi.jenkins import Jenkins
from app import socketio

url = os.getenv('JENKINS_URL')
username = os.getenv('JENKINS_USERNAME')
password = os.getenv('JENKINS_PASSWORD')
token = os.getenv('JENKINS_TOKEN')


# 判断上一次是否构建成功
@socketio.on('baseline', namespace='/task')
def get_jenkins_job(job_name, room):
    global url, username, password
    url = url
    J = Jenkins(url, username=username, password=password)
    job = J[job_name]
    jenkins_last_build = job.get_last_build().is_good()
    if jenkins_last_build:
        socketio.emit('baseline', '上一次应用构建成功\n', namespace='/task', room=room)
    else:
        socketio.emit('baseline', '上一次应用构建失败\n', namespace='/task', room=room)
    jenkins_build_number = job.get_next_build_number()
    console_url = job.url + str(jenkins_build_number) + '/console\n'
    socketio.emit('baseline',
                  'Jenkins控制台： ' + console_url,
                  namespace='/task',
                  room=room)


# request触发Jenkins远程构建
def build_by_token(job_name):
    global url, username, password
    datas = {'username': username, 'password': password, 'token': token}
    build_url = url + '/job/' + job_name + '/build'
    r = requests.post(build_url, data=datas)
    return r.ok


# request触发Jenkins远程参数构建
@socketio.on('baseline', namespace='/task')
def build_with_parameters(job_name, room, **kw):
    global url, username, password, token
    kw.update({'token': token})
    build_url = url + '/job/' + job_name + '/buildWithParameters'
    
    r = requests.post(build_url, data=kw)
    socketio.emit('baseline',
                  '***正在更新'+ job_name + '***',
                  namespace='/task',
                  room=room)
    return r.ok
