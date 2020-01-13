import os,shutil

from flask_login import UserMixin, AnonymousUserMixin
from .. import login_manager
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


class User(UserMixin, db.Model):
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
    
    # 将密码加密存储
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

    # can() 方法在请求和赋予角色这两种权限之间进行位与操作。如果角色中包含请求的所有权限位，则返回True
    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

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

    def is_administrator(self):
        return self.can(Permission.administer)

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
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
      return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


'''
权限分配：
更新，重更基线    0b00000001（0x01）
更新基线状态      0b00000010（0x02）
删除基线          0b00000100（0x04）
后台管理          0b00001000（0x08）
管理员            0b10000000（0x80）
'''


class Permission:
    update_baseline = 0x01
    update_baseline_status = 0x02
    delete_baseline = 0x04
    backend_manage = 0x08
    administer = 0x80


'''
角色划分：
开发
测试
协管员
管理员
'''


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',back_populates='role')

    @staticmethod
    def insert_roles():
        roles = {
            'Developer': (Permission.update_baseline, False),
            'Tester': (Permission.update_baseline_status, False),
            'Moderator': (Permission.update_baseline |
                Permission.update_baseline_status |
                Permission.delete_baseline | Permission.backend_manage, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


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