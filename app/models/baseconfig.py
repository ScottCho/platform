'''
@Author: your name
@Date: 2020-04-16 11:56:31
@LastEditTime: 2020-04-17 14:45:05
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /platform/app/models/baseconfig.py
'''
import os

from flask import render_template

from app import db, flask_app
from app.utils.ansible_api import ansible_playbook, exec_shell


# 状态表
#登录协议
class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True)
    attribute = db.Column(db.String(64), index=True)
    
    requirements = db.relationship('IssueRequirement', back_populates='status')
    bugs = db.relationship('IssueBug', back_populates='status')
    tasks = db.relationship('IssueTask', back_populates='status')
    baselines = db.relationship('Baseline', back_populates='status')
    
    def __repr__(self):
        return '<Status.name %r>' % self.name



# 标签: 1.功能完善 2.待确认 3.新增需求 4.解释性问题 5.重复问题 6.需求变更
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False,unique=True, index=True)
    attribute = db.Column(db.String(64), index=True)

    requirements = db.relationship('IssueRequirement', back_populates='tag')
    bugs = db.relationship('IssueBug', back_populates='tag')

# 软件
class Software(db.Model):
    __tablename__ = 'softwares'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False,unique=True, index=True)
    playbook = db.Column(db.String(128))

#  后台任务和服务器的关联关系
bgtask_ass_server = db.Table('bgtask_ass_server',
    db.Column('bgtask_id', db.Integer, db.ForeignKey(
        'bgtasks.id'), primary_key=True),
    db.Column('server_id', db.Integer, db.ForeignKey(
        'servers.id'), primary_key=True)
)

'''
任务id： 10
name： install nginx
target_serverr: 192.168.0.10
'''

# 后台任务表
class BgTask(db.Model):
    __tablename__ = 'bgtasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    software_id = db.Column(db.Integer,db.ForeignKey('softwares.id'))
    servers = db.relationship('Server', secondary='bgtask_ass_server', back_populates='bgtasks')
    software = db.relationship('Software')

    # 部署任务
    def run_playbook(self):
        _ = [server.ip for server in self.servers]
        server_ips = ','.join(_)
        playbook = self.software.playbook
        task_id = self.id
        # /Code/githup/platform/app/templates/playbook/nginx_playbook.yml
        playbook_template = render_template('ansible/playbook/'+playbook,server_ips=server_ips)
        playbook_path = os.path.join('/etc/ansible/playbook',playbook)
        with open(playbook_path, 'w') as f:
            f.write(playbook_template)
        ansible_playbook('playbook',task_id,playbook_path)
        return '任务ID: '+str(task_id)
