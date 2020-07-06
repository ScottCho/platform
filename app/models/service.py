# -*- coding:UTF-8 -*-
# AUTHOR: Zhao Yong
# FILE: /Code/githup/platform/app/models/service.py
# DATE: 2020/04/29 Wed

from flask import g
from app.utils.encryp_decrypt import decrypt, encrypt
from app.utils.jenkins import build_by_token, get_jenkins_job
from .. import db


# 数据库实例
class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instance = db.Column(db.String(80), nullable=False)
    port = db.Column(db.String(32), nullable=False)
    project = db.Column(db.String(80), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    mark = db.Column(db.String(80))
    project = db.relationship('Project')
    schemas = db.relationship('Schema', back_populates='instance')
    credence_id = db.Column(db.Integer, db.ForeignKey('credences.id'))
    credence = db.relationship('Credence', back_populates='databases')
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    server = db.relationship('Server')
    project = db.relationship('Project', back_populates='databases')


# 数据库的Schema
class Schema(db.Model):
    __tablename__ = 'db_schemas'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    instance_id = db.Column(db.Integer, db.ForeignKey('database.id'))
    app = db.relationship('App', uselist=False)  # 建立与APP一对一的关系
    instance = db.relationship('Database', back_populates='schemas')

    # 读取密码
    @property
    def password(self):
        password = decrypt(self.password_hash)
        return str(password)

    # 将密码加密存储
    @password.setter
    def password(self, password):
        s = encrypt(password)
        self.password_hash = s


class App(db.Model):
    __tablename__ = 'apps'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    log_dir = db.Column(db.String(80), nullable=False)
    jenkins_job_dir = db.Column(db.String(256))
    source_dir = db.Column(db.String(256))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    project = db.relationship('Project', back_populates='apps')
    env_id = db.Column(db.Integer, db.ForeignKey('envs.id'))
    env = db.relationship('Env', back_populates='apps')
    subsystem_id = db.Column(db.Integer, db.ForeignKey('subsystems.id'))
    subsystem = db.relationship('Subsystem')
    baselines = db.relationship('app.models.version.Baseline',
                                back_populates='app')
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    server = db.relationship('Server')
    schema_id = db.Column(db.Integer, db.ForeignKey('db_schemas.id'))
    schema = db.relationship('Schema')
    credence_id = db.Column(db.Integer, db.ForeignKey('credences.id'))
    credence = db.relationship('Credence', back_populates='apps')
    port = db.Column(db.String(16))  # 应用访问端口
    deploy_dir = db.Column(db.String(256))  # 部署目录
    jenkins_job_name = db.Column(db.String(256))  # jenkin job的名字
    alias = db.Column(db.String(32))  # 项目别名
    context = db.Column(db.String(64))  # 应用访问的上下文

    def full_release(self):
        build_by_token(self.jenkins_job_name)
        console_url = get_jenkins_job(self.jenkins_job_name,
                                      str(g.current_user.id))
        return console_url


class Subsystem(db.Model):
    __tablename__ = 'subsystems'
    id = db.Column(db.Integer, primary_key=True)
    en_name = db.Column(db.String(32), nullable=False)
    zh_name = db.Column(db.String(32), nullable=False)


class Env(db.Model):
    __tablename__ = 'envs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    apps = db.relationship('App', back_populates='env')
    packages = db.relationship('Package', back_populates='env')