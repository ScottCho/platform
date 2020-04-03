import os,shutil

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask import current_app

from .. import db

group = db.Table('group',
    db.Column('proj_id', db.Integer, db.ForeignKey(
        'projects.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    role = db.relationship('Role',back_populates='users')
    projects = db.relationship(
        'Project', secondary='group', back_populates='users')
    requirements = db.relationship('IssueRequirement',back_populates='assignee')
    bugs = db.relationship('IssueBug',back_populates='assignee')
    tasks = db.relationship('IssueTask',back_populates='assignee')
    
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 使用token验证注册用户
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True


    #is_active属性为false，flask_login将拒绝用户登录
    @property
    def is_active(self):
        return self.active

    def block(self):
        self.active = False
        db.session.commit()

    def unblock(self):
        self.active = True
        db.session.commit()


    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
      return '<User %r>' % self.username



class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User',back_populates='role')

    def __repr__(self):
        return '<Role %r>' % self.name





class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    zh_name = db.Column(db.String(128))
    source_dir = db.Column(db.String(80))
    target_dir = db.Column(db.String(80))
    switch = db.Column(db.Boolean, default=True)
    apps = db.relationship('App',back_populates='project')
    users = db.relationship('User',secondary='group',back_populates='projects')
    packages = db.relationship('Package',back_populates='project')
    requirements = db.relationship('IssueRequirement',back_populates='project')
    bugs = db.relationship('IssueBug',back_populates='project')
    tasks = db.relationship('IssueBug',back_populates='project')


    def __repr__(self):
        return '<Project.name %r>' % self.name

    #重建打包的目录
    def rebuild_relase_directory(self):
        target_dir = self.target_dir
        APP_dir=os.path.join(target_dir,'APP')
        DB_dir=os.path.join(target_dir,'DB')
        log_dir=os.path.join(target_dir,'LOG')
        target_sqldir = os.path.join(DB_dir, 'SQL')
        target_pckdir = os.path.join(DB_dir, 'PCK')
        target_rollbackdir = os.path.join(DB_dir, 'ROLLBACK')
        try:
            if os.path.exists(DB_dir):
                shutil.rmtree(DB_dir)
            os.makedirs(target_sqldir)
            os.mkdir(target_pckdir)
            os.mkdir(target_rollbackdir)
            if os.path.exists(log_dir):
                shutil.rmtree(log_dir)
            os.mkdir(log_dir)
            if os.path.exists(APP_dir):
                shutil.rmtree(APP_dir)
            os.mkdir(APP_dir)
        except OSError:
            pass
