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
from celery import Celery,platforms
from config import config
from flask_socketio import SocketIO,emit
from flask_cors import CORS, cross_origin



db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

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

# 提供跨域支持
CORS(flask_app)
# 初始化SocketIO
socketio = SocketIO(flask_app)

#初始化celery
celery = make_celery(flask_app)



#初始化数据库
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

from app.models.service import Database, Schema,App,Subsystem,Env
from app.models.auth import Project, Role, User
from app.models.version import Baseline
from app.models.issues import IssueSource, IssueCategory,  IssueModule, IssueReproducibility, \
    IssuePriority, IssueSeverity, IssueStatus, IssueTag, IssueRequirement, IssueBug, IssueTask, \
        bug_ass_baseline, requirement_ass_baseline, task_ass_baseline

@flask_app.shell_context_processor
def make_shell_context():
    return dict(db=db, Project=Project, Database=Database, App=App, Baseline=Baseline,
        Subsystem=Subsystem,Env=Env,Role=Role,IssueTask=IssueTask,IssueStatus=IssueStatus)



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

def ack():
    print('message was received!')

#处理接收到的客户端信息
@socketio.on('connect event',namespace='/task')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    emit('event2',str(json),namespace='/task',callback=ack)



@flask_app.route('/task')
def start_background_task():
    # remote_socket_shell()
    socket_shell('ping -c5 qq.com')
    return 'Started'

@flask_app.route('/socket')
@cross_origin(allow_headers=['Content-Type'])
def socket():
        return render_template('apis/v2/socketio.html')


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
            file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], filename))
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
    return send_from_directory(flask_app.config['UPLOAD_FOLDER'],
                               filename)


@flask_app.route('/listfile')
def list_file():
    files = os.listdir(flask_app.config['UPLOAD_FOLDER'])
    return render_template('apis/v2/issue/list_file.html',files=files)


# 测试csv
import csv, sys
@flask_app.route('/csv')
def read_csv():
    row=''
    filename = '/data/frog/issue/test.csv'
    with open(filename, newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # print(row)                # OrderedDict([('name', 'aa'), ('password', '22')])
            # print(row['所属项目'])    # 返回：aa bb
            number=row['编号']
            summary=row['任务名称']
            description=row['任务描述']
            startdate = row['实际开始'] if row['实际开始'] != '0000-00-00' else None
            enddate = row['完成时间'] if row['完成时间'] != '0000-00-00' else None
            deadline = row['截止日期'] if row['截止日期'] != '0000-00-00' else None
            manhour = row['最初预计'] 
            status_name = row['任务状态']
            status_id = IssueStatus.query.filter_by(name=status_name).one().id
            requirement_summary = row['相关需求']
            if requirement_summary:
                requirement_id = requirement_summary.split('#')[-1].strip(')')
            else:
                requirement_id = None
            assignee_name = '赵勇'
            assignee_id = User.query.filter_by(username=assignee_name).one().id
            priority_id = row['优先级'] if row['优先级'] != '' else None
            itask = IssueTask(number=number,
			                    summary = summary,
			                    description = description,
			                    startdate = startdate,
                                enddate = enddate,
                                deadline = deadline,
                                manhour = manhour,
                                status_id=status_id,
                                requirement_id=requirement_id,
                                assignee_id =assignee_id,
                                priority_id=priority_id
			)
            db.session.add(itask)
            db.session.commit()
    return str(row['所属项目'])




