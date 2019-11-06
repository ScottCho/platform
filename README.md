系统管理平台
=============================================

        1. 克隆项目
        git clone git@github.com:ScottCho/platform.git

        2. 安装虚拟环境
        pip3 install pipenv
        pipenv install

        3. 初始化数据库
        mysql> create database platform character set 'utf8' collate 'utf8_bin';
        mysql> create user 'scott'@'%' identified by 'tiger';
        flask db init
        flask db migrate
        flask db upgrade
        Role.insert_roles()

        4. 设置环境变量文件.env
        MAIL_PASSWORD='Scott@qq123'
        MAIL_USERNAME=xxx@xxx.com.cn'
        FLASK_CONFIG='production'
        MAIL_SERVER='smtp.exmail.qq.com'
        MAIL_DEFAULT_SENDER='xxx@xxx.com.cn'
        ADMIN_EMAIL=xxxx@xxx.com.cn
        DATABASE_URL='mysql+pymysql://scott:tiger@xxxx:3306/platform?charset=utf8mb4'
        JENKINS_URL='http://xxx:8080/jenkins'
        JENKINS_TOKEN='xxx'
        JENKINS_USERNAME='admin'
        JENKINS_PASSWORD='xxx'
        CELERY_BROKER_URL=pyamqp://guest:guest@rabbitmq:5672//
        CELERY_RESULT_BACKEND = 'redis://xxxx:6379'

        5. 启动实例
        gunicorn app:flask_app -b 0.0.0.0:5000 -w 3 -D -p /tmp/app5000.pid --log-file /tmp/app5000.log

        6. 启动celery
        调试： celery -A app.celery worker -l info
        后台启动：
        celery multi start w1 -A app.celery  -l info --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log
        重启：
        celery multi restart w1 -A app.celery  -l info --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log 
