# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from celery import Celery, platforms
from config import config, mail_handler, handler
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
import redis

#  init redis
redis_cli = redis.StrictRedis(host=os.getenv('REDIS_HOSt', '127.0.0.1'),
                              port=os.getenv('REDIS_PORT', 6379),
                              db=os.getenv('REDIS_DB', 0),
                              decode_responses=True)

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

platforms.C_FORCE_ROOT = True


def make_celery(app):
    celery = Celery(app.import_name,
                    service=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'],
                    include=['app.tasks'])
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


#创建和配置flask_app
ENV = os.getenv('FLASK_CONFIG') or 'default'
flask_app = Flask(__name__, instance_relative_config=True)
flask_app.config.from_object(config[ENV])
config[ENV].init_app(flask_app)
# flask_app.logger.setLevel(logging.INFO)
if not flask_app.debug:
    flask_app.logger.addHandler(mail_handler)
flask_app.logger.addHandler(handler)

# 提供跨域支持
CORS(flask_app)
# 初始化SocketIO
socketio = SocketIO(flask_app, ping_timeout=300)

# 初始化celery
celery = make_celery(flask_app)


# 初始化数据库
db.init_app(flask_app)
migrate.init_app(flask_app, db)
mail.init_app(flask_app)

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


# 每次请求前验证token，并将user和projet存储到g中
from app.apis.v2.auth import get_token, validate_token


@flask_app.before_request
def get_project():
    print(request.url_rule)
    token_type, token = get_token()
    if token:
        if validate_token(token):
            key = f'user:{g.current_user.id}'
            try:
                project_id = redis_cli.hmget(key, 'project_id')[0]
            except Exception:
                g.current_project = None
            else:
                project = Project.query.get(project_id)
                g.current_project = project
        else:
            g.current_project = None
    elif request.url_rule == '/api/oauth/token':
        g.current_project = None
    else:
        print('Token不存在')


from app.models.baseconfig import Status, Tag, BgTask
from app.models.service import Database, Schema, App, Subsystem, Env
from app.models.auth import Project, Role, User
from app.models.version import Baseline
from app.models.issues import IssueSource, IssueCategory,  IssueModule, \
                              IssueReproducibility, IssuePriority, IssueSeverity, \
                              IssueRequirement, IssueBug, IssueTask, \
                              bug_ass_baseline, requirement_ass_baseline, task_ass_baseline


@flask_app.shell_context_processor
def make_shell_context():
    return dict(db=db,
                Project=Project,
                Database=Database,
                App=App,
                Baseline=Baseline,
                Subsystem=Subsystem,
                Env=Env,
                Role=Role,
                IssueTask=IssueTask,
                BgTask=BgTask,
                Status=Status)


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
col_headers = ['日期', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
row_headers = ['用户{}'.format(i) for i in range(1, 11)]
import csv, os
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
    csv_file = os.path.join(
        'C:\\Users\\scott\\Documents\\GitHub\\platform\\app', 'statistics.csv')
    write_csv(csv_file, col_headers, rows_data)

    send_email(['张三 <scottcho@qq.com>'],
               '英语成绩',
               'mail/panda.html',
               attachments=[csv_file],
               cc=['李四 <zhaoysz@sinosoft.com.cn>'],
               col_headers=col_headers,
               row_headers=row_headers,
               rows_data=rows_data)
    return render_template('mail/panda.html',
                           col_headers=col_headers,
                           row_headers=row_headers,
                           rows_data=rows_data)


from app.utils.execute_cmd import remote_socket_shell, socket_shell


def ack():
    print('message was received!')


@socketio.on('connect')
def test_connect():
    print({'data': 'Connected'})
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@flask_app.route('/task')
def start_background_task():
    # remote_socket_shell()
    print('开始')
    from app.utils.execute_cmd import socket_shellzz
    socket_shellzz('sh /tmp/a.sh')
    return 'Started'


@flask_app.route('/socket')
@cross_origin(allow_headers=['Content-Type'])
def socket():
    return render_template('apis/v2/socketio.html')

from flask_socketio import join_room, leave_room, close_room, emit, send

@socketio.on('join', namespace='/task')
def on_join(data):
    room = str(data['room'])
    join_room(room)
    print('join room: '+room)
    emit(room + ' has entered the room.', room=room)

@socketio.on('leave', namespace='/task')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit(room + ' has left the room.', room=room)


@socketio.on('close', namespace='/task')
def on_close(data):
    room = data['room']
    print('close room: '+room)
    close_room(room)


### 测试文件上传
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'xls', 'csv', 'md'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@flask_app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'],
                                   filename))
            return redirect(url_for('list_file'))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


from flask import send_from_directory


@flask_app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(flask_app.config['UPLOAD_FOLDER'], filename)


@flask_app.route('/listfile')
def list_file():
    files = os.listdir(flask_app.config['UPLOAD_FOLDER'])
    return render_template('apis/v2/issue/list_file.html', files=files)