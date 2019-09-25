系统管理平台
=============================================

        1. 克隆项目
        git clone git@github.com:ScottCho/platform.git

        2. 安装虚拟环境
        python3 -m venv venv

        3. 激活虚拟环境
        windows： venv\Scripts\activate
        Linux: . venv/bin/activate

        4. 安装依赖文件
        pip freeze > requirements.txt
        pip install -r requirements.txt

        5. 初始化数据库
        mysql> create database platform character set 'utf8' collate 'utf8_bin';
        mysql> create user 'platformadmin'@'%' identified by 'platform';
        python manage.py db migrate
        python manage.py db upgrade

        6. 设置环境变量
        export MAIL_USERNAME = 'xxx@xxx'
        export MAIL_PASSWORD = 'youpassword'
        export FLASK_CONFIG = 'production'
        export DATABASE_URL = 'you db url'

        7. 启动实例
        gunicorn app:flask_app -b 0.0.0.0:5001 -w 3 -D -p /tmp/app.pid --log-file /tmp/app.log

        8. 启动celery
        调试： celery -A app.celery worker -l info
        后台启动：
        celery multi start w1 -A app.celery  -l info --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log
        重启：
        celery multi restart w1 -A app.celery  -l info --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log

        9. 插入角色
        Role.insert_roles()


