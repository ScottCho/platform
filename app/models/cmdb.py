# -*- coding:UTF-8 -*-
# AUTHOR: Zhao Yong
# FILE: /Code/githup/platform/app/models/cmdb.py
# DATE: 2020/04/29 Wed

from .. import db
from app.utils.encryp_decrypt import decrypt, encrypt

# 机器组和机器的连接表
server_groups = db.Table(
    'server_ass_group',
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('server_groups.id'), primary_key=True)
)


# 机器
class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(80), nullable=False)
    hostname = db.Column(db.String(80), nullable=False)
    ip = db.Column(db.String(80), nullable=False)
    credence_id = db.Column(db.Integer, db.ForeignKey('credences.id'))
    os = db.Column(db.String(80))
    remarks =  db.Column(db.Text())
    credence = db.relationship('Credence', back_populates='servers')
    groups = db.relationship('ServerGroup',
                             secondary=server_groups, back_populates='servers')

    bgtasks = db.relationship('BgTask', secondary='bgtask_ass_server', back_populates='servers')

    def __repr__(self):
        return '<Server.alias %r>' % self.alias


# 凭证
class Credence(db.Model):
    __tablename__ = 'credences'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    agreement_id = db.Column(db.Integer, db.ForeignKey('agreements.id'))
    agreement = db.relationship('Agreement')
    port = db.Column(db.Integer, default=22)
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(120), nullable=False)
    ssh_key = db.Column(db.Text)
    # agent_ip = db.Column(db.String(20))
    # agent_port = db.Column(db.String(10))
    # agent_password = db.Column(db.String(80))
    servers = db.relationship('Server', back_populates='credence')
    apps = db.relationship('App', back_populates='credence')
    databases = db.relationship('Database', back_populates='credence')

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

    def __repr__(self):
        return '<Credence.name %r>' % self.name


# 登录协议
class Agreement(db.Model):
    __tablename__ = 'agreements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    credences = db.relationship('Credence')

    def __repr__(self):
        return '<Agreement.name %r>' % self.name


# 机器分组
class ServerGroup(db.Model):
    __tablename__ = 'server_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    servers = db.relationship('Server',
                              secondary=server_groups, back_populates='groups')


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(128))
