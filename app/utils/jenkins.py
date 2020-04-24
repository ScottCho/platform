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

url = os.getenv('JENKINS_URL')
username = os.getenv('JENKINS_USERNAME')
password = os.getenv('JENKINS_PASSWORD')
token = os.getenv('JENKINS_TOKEN')

#判断最近一次构建是否成功
def get_jenkins_job(job_name):
    global url,username,password
    url = url
    J = Jenkins(url,username=username,password=password)
    job=J[job_name]
    return job
    #get_last_build().is_good()

#request触发Jenkins远程构建
def build_by_token(job_name):
    global url,username,password
    datas = {'username':username, 'password':password, 'token':token}
    build_url =  url+'/job/'+job_name+'/build'
    r = requests.post(build_url,data=datas)
    return r.ok

#request触发Jenkins远程参数构建
def build_with_parameters(job_name,**kw):
    global url,username,password,token
    kw.update({'token':token})
    build_url =  url+'/job/'+job_name+'/buildWithParameters'
    print(build_url,kw)
    r = requests.post(build_url,data=kw)
    return r.ok
