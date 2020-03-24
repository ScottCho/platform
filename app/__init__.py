 #!/usr/bin/python
#-*- coding: UTF-8 -*-
import os
import subprocess
from threading import Lock
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager,current_user,logout_user
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect
from celery import Celery,platforms
from config import config
from flask_socketio import SocketIO


db = SQLAlchemy()
mail = Mail()
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

# 初始化SocketIO
socketio = SocketIO(flask_app)

#初始化celery
celery = make_celery(flask_app)



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
from app.models.issues import IssueSource, IssueCategory,  IssueModule, IssueReproducibility, \
    IssuePriority, IssueSeverity, IssueStatus, IssueTag, IssueRequirement, IssueBug, IssueTask, \
        bug_ass_baseline, requirement_ass_baseline, task_ass_baseline

@flask_app.shell_context_processor
def make_shell_context():
    return dict(db=db, Project=Project, Database=Database, App=App, Baseline=Baseline,
        Subsystem=Subsystem,Env=Env,Role=Role)


###### 测试
rows_data = [
    [34, 72, 38, 30, 75, 48, 75],
    [6, 24, 1, 84, 54, 62, 60],
    [28, 79, 97, 13, 85, 93, 93],
    [27, 71, 40, 17, 18, 79, 90],
    [88, 25, 33, 23, 67, 1, 59],
    [24, 100, 20, 88, 29, 33, 38],
    [6, 57, 88, 28, 10, 26, 37],
    [52, 78, 1, 96, 26, 45, 47],
    [60, 54, 81, 66, 81, 90, 80],
    [70, 5, 46, 14, 71, 19, 66],
]
col_headers = ['日期', '周一', '周二', '周三',
               '周四', '周五', '周六', '周日']
row_headers = ['用户{}'.format(i) for i in range(1, 11)]





import csv,os
from app.localemail import send_email

def write_csv(csv_file, headers, rows):
    f = open(csv_file, 'wt')
    writer = csv.writer(f)
    writer.writerow(headers)
    for index, row in enumerate(rows):
        writer.writerow([row_headers[index]] + row)
    f.close()

@flask_app.route('/test')
def test():
    csv_file = os.path.join('C:\\Users\\scott\\Documents\\GitHub\\platform\\app', 'statistics.csv')
    write_csv(csv_file, col_headers, rows_data)

    send_email(['张三 <scottcho@qq.com>'], '英语成绩',
               'mail/panda.html', attachments=[csv_file],cc=['李四 <zhaoysz@sinosoft.com.cn>'], 
               col_headers=col_headers,
               row_headers=row_headers,
               rows_data=rows_data
                )
    
    return render_template('mail/panda.html',col_headers=col_headers,
               row_headers=row_headers,
               rows_data=rows_data)




from app.utils.execute_cmd import remote_socket_shell,socket_shell


@flask_app.route('/task')
def start_background_task():
    #remote_socket_shell()
    socket_shell('ping -c5 qq.com')
    return 'Started'

@flask_app.route('/socket')
def socket():
        return render_template('apis/v2/socketio.html')

