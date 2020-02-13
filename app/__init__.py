 #!/usr/bin/python
#-*- coding: UTF-8 -*-
import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_mail import Mail
from flask_login import LoginManager,current_user,logout_user
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect
from celery import Celery,platforms
from config import config


db = SQLAlchemy()
mail = Mail()
moment = Moment()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_message = '请在这登录注册的用户'
login_manager.login_view = 'auth.login'

platforms.C_FORCE_ROOT = True

def make_celery(app):
    celery = Celery(
        app.import_name,
        service=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        include=['app.tasks']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

#创建和配置flask_app
ENV = os.getenv('FLASK_CONFIG') or 'default'
flask_app = Flask(__name__,instance_relative_config=True)
flask_app.config.from_object(config[ENV])
config[ENV].init_app(flask_app)
flask_app.logger.setLevel(logging.INFO)


#初始化celery
celery = make_celery(flask_app)


#时间处理
moment.init_app(flask_app)
#初始化数据库
db.init_app(flask_app)
migrate.init_app(flask_app, db)
mail.init_app(flask_app)
login_manager.init_app(flask_app)
# csrf.init_app(flask_app)


# 注册用户认证蓝图
from .auth import auth_bp
flask_app.register_blueprint(auth_bp, url_prefix='/auth')

# 注册版本管理蓝图
from app.version import version_bp
flask_app.register_blueprint(version_bp, url_prefix='/version')

# 注册日志蓝图
from .log import log_bp
flask_app.register_blueprint(log_bp, url_prefix='/log')

# 注册服务管理蓝图
from .service import service_bp
flask_app.register_blueprint(service_bp, url_prefix='/service')

# 注册后台管理蓝图
from .backstage import backstage_bp
flask_app.register_blueprint(backstage_bp,url_prefix='/backstage')

# 注册api蓝图api v1
from .apis.v1 import api_v1
flask_app.register_blueprint(api_v1, url_prefix='/api/v1')

# 导入api v2
import app.apis.v2
# 注册api蓝图api v2
from .apis.v2 import api_v2
flask_app.register_blueprint(api_v2, url_prefix='/api')




# 首页视图
@flask_app.route('/')
def index():
    return render_template('index.html')

from app.models.service import Database, Schema,App,Subsystem,Env
from app.models.auth import Project, Role
from app.models.version import Baseline
@flask_app.shell_context_processor
def make_shell_context():
    return dict(db=db, Project=Project, Database=Database, App=App, Baseline=Baseline,
        Subsystem=Subsystem,Env=Env,Role=Role)


# 错误处理
# @flask_app.errorhandler(400)
# def bad_request(e):
#     return render_template('errors/400.html'), 400


# @flask_app.errorhandler(403)
# def forbidden(e):
#     return render_template('errors/403.html'), 403


# @flask_app.errorhandler(404)
# def page_not_found(e):
#     return render_template('errors/404.html'), 404


# @flask_app.errorhandler(413)
# def request_entity_too_large(e):
#     return render_template('errors/413.html'), 413


# @flask_app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('errors/500.html'), 500


# @flask_app.errorhandler(CSRFError)
# def handle_csrf_error(e):
#     return render_template('errors/400.html', description=e.description), 400