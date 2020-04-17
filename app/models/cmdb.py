'''
@Author: your name
@Date: 2020-04-17 10:34:07
@LastEditTime: 2020-04-17 15:26:38
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /platform/app/models/cmdb.py
'''
from .. import db
from app.utils.encryp_decrypt import decrypt,encrypt

#机器组和机器的连接表
server_servergroubs = db.Table('server_ass_groub',
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True),
    db.Column('servergroub_id', db.Integer, db.ForeignKey('servergroubs.id'), primary_key=True)
)

#机器
class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(80), nullable=False)
    hostname = db.Column(db.String(80), nullable=False)
    ip = db.Column(db.String(80), nullable=False)
    state = db.Column(db.Boolean, default=False)
    credence_id = db.Column(db.Integer,db.ForeignKey('credences.id'))
    os = db.Column(db.String(80))
    remarks =  db.Column(db.Text())
    credence = db.relationship('Credence',back_populates='servers')
    
    servergroubs = db.relationship('ServerGroub',
        secondary=server_servergroubs,back_populates='servers'
        )
    bgtasks = db.relationship('BgTask', secondary='bgtask_ass_server', back_populates='servers')

    def __repr__(self):
        return '<Server.alias %r>' % self.alias

#凭证
class Credence(db.Model):
    __tablename__ = 'credences'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True,nullable=False)
    agreement_id = db.Column(db.Integer,db.ForeignKey('agreements.id'))
    agreement = db.relationship('Agreement')
    port = db.Column(db.Integer ,default=22)
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(120), nullable=False)
    ssh_key = db.Column(db.Text)
    # agent_ip = db.Column(db.String(20))
    # agent_port = db.Column(db.String(10))
    # agent_password = db.Column(db.String(80))
    servers = db.relationship('Server',back_populates='credence')
    apps = db.relationship('App',back_populates='credence')
    databases = db.relationship('Database',back_populates='credence')


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

#登录协议
class Agreement(db.Model):
    __tablename__ = 'agreements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    credences = db.relationship('Credence')
    def __repr__(self):
        return '<Agreement.name %r>' % self.name

#机器组
class ServerGroub(db.Model):
    __tablename__ = 'servergroubs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    servers = db.relationship('Server',
        secondary=server_servergroubs,back_populates='servergroubs'
        )


