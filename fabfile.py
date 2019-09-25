# -*- coding: utf-8 -*-

from fabric import Connection,task
from invoke import run


@task
def restart_app(c):
	if run('test -f /tmp/platform.pid', warn=True).ok:
		pid = run('cat /tmp/platform.pid').stdout.strip()
		run('kill -9 {};rm /tmp/platform.pid'.format(pid))
	else:
		run ('echo pid file not exists!')
	run('gunicorn manage:flask_app -b 0.0.0.0:5001 -w 3 -D -p /tmp/platform.pid --log-file /tmp/platform.log')
	if run('test -d /var/log/celery/', warn=True).ok:
		run('rm -rf /var/log/celery/*')
		run('celery multi restart w1 -A app.celery  -l info --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log')


@task
def backup_db(c):
	c.run('hostname')
