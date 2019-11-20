import logging
import subprocess
import threading

from flask import (current_app, flash, redirect, render_template, request,
                   url_for)
from flask_login import login_required

from app.decorators import admin_required, permission_required
from app.tasks import remote_shell
from app.utils.redirect_back import redirect_back

from .. import db
from ..models.auth import Permission, Project
from ..models.machine import Agreement, Credence, Machine
from ..models.service import App, Database
from . import service_bp


#管理应用
@service_bp.route('/manage/app')
@login_required
def manage_app():
    page = request.args.get('page', 1, type=int)
    per_page=current_app.config['FLASKY_BASELINES_PER_PAGE']
    filter_rule = request.args.get('filter', 'all')
    if filter_rule == 'all':
        filtered_apps = App.query
    else:
    	filtered_apps = App.query.filter_by(project_id=filter_rule)
    pagination = filtered_apps.order_by(App.id.desc()).paginate(
        page, per_page,
        error_out=False)
    apps = pagination.items
    projects = Project.query.all()
    return render_template('service/manage_app.html', apps=apps,projects=projects,
                           pagination=pagination)   


#操作应用
@service_bp.route('/ctl/app/<action>/<int:id>',methods=('GET','POST'))
@login_required
@permission_required(Permission.backend_manage)
def ctl_app(id,action):
	app = App.query.get_or_404(id)
	env = app.env.name.lower()
	subsystem = app.subsystem.en_name.lower()
	command='sh /usr/local/sbin/weblogic_{}.sh {} {}'.format(env,action,subsystem)
	result = remote_shell(app.host,command,username=app.username,password=app.password)
	print(result)
	flash('已经执行命令，请勿重复点击','danger')
	return redirect(url_for('service.manage_app'))

@service_bp.route('/dbview/')
@login_required
def dbview():
	dblist = Database.query.all()
	return render_template('service/dbmanage.html',dblist=dblist)

#管理数据库
@service_bp.route('/dbmanage/<instance>/<action>',methods=('GET','POST'))
@login_required
@permission_required(Permission.backend_manage)
def dbmanage(instance,action):
	db = Database.query.filter_by(instance=instance).first_or_404()
	command='sh /usr/local/sbin/restart_oracle.sh {} {}'.format(action,instance)
	logging.info('*'*8+'execute command ' + command + ' on oracle'+'@'+db.host+'*'*8)
	result = remote_shell(db.host,command,username=db.username,password=db.password)
	flash('已经执行命令，请勿重复点击','danager')
	return redirect(url_for('service.dbview'))

#机器管理
@service_bp.route('/machine/manage')
@login_required
@permission_required(Permission.backend_manage)
def manage_machine():
	page = request.args.get('page', 1, type=int)
	pagination = Machine.query.order_by(Machine.id.desc()).paginate(
		page, per_page=current_app.config['FLASKY_BASELINES_PER_PAGE'],
		error_out=False)
	machines = pagination.items
	threads = []
	for machine in machines:
		if subprocess.call(["ping", "-c", "1", machine.ip]) == 0:
			machine.status = True
		else:
			machine.status = False
	return render_template('service/manage_machine.html',page=page, pagination=pagination,machines=machines)


#添加机器
@service_bp.route('/machine/new',methods=('GET','POST'))
@login_required
@permission_required(Permission.backend_manage)
def new_machine():
	if request.method == 'POST':
		alias = request.form.get("alias")
		credence_id = request.form.get("credence_id")
		hostname = request.form.get("hostname")
		ip = request.form.get("ip")
		remarks = request.form.get("remarks")
		os = request.form.get("os")
		machine = Machine(alias=alias,
			credence_id=credence_id,
			hostname=hostname,
			ip=ip,
			os=os,
			remarks=remarks
			)
		db.session.add(machine)
		db.session.commit()
		flash('添加机器成功.','warning')
	credences = Credence.query.all()
	return render_template('service/add_machine.html',credences=credences)

#删除机器
@service_bp.route('/machine/<int:machine_id>/delete')
@login_required
@permission_required(Permission.backend_manage)
def delete_machine(machine_id):
	machine = Machine.query.get_or_404(machine_id)
	db.session.delete(machine)
	db.session.commit()
	flash('删除机器成功.','warning')
	return redirect_back()

#查看机器信息
@service_bp.route('/machine/<int:machine_id>/view')
@login_required
@permission_required(Permission.backend_manage)
def view_machine(machine_id):
	machine = Machine.query.get_or_404(machine_id)
	return render_template("service/view_machine.html",machine=machine)

#修改机器信息
@service_bp.route('/machine/<int:machine_id>/edit',methods=('GET','POST'))
@login_required
@permission_required(Permission.backend_manage)
def edit_machine(machine_id):
	machine = Machine.query.get_or_404(machine_id)
	if request.method == 'POST':
		machine.alias = request.form.get("alias")
		machine.credence_id = request.form.get("credence_id")
		machine.hostname = request.form.get("hostname")
		machine.ip = request.form.get("ip")
		machine.os = request.form.get("os")
		machine.remarks = request.form.get("remarks")
		db.session.add(machine)
		db.session.commit()
		flash('修改机器信息成功.','warning')
	machine = Machine.query.get_or_404(machine_id)
	credences = Credence.query.all()
	return render_template('service/edit_machine.html',credences=credences,machine=machine)

#凭证列表显示
@service_bp.route('/credence/manage')
@login_required
@permission_required(Permission.backend_manage)
def manage_credence():
	page = request.args.get('page', 1, type=int)
	pagination = Credence.query.order_by(Credence.id.desc()).paginate(
		page, per_page=current_app.config['FLASKY_BASELINES_PER_PAGE'],
		error_out=False)
	credences = pagination.items
	return render_template('service/manage_credence.html',page=page, pagination=pagination,credences=credences)

#添加凭证
@service_bp.route('/credence/new',methods=('GET','POST'))
@login_required
@permission_required(Permission.backend_manage)
def new_credence():
	if request.method == 'POST':
		name = request.form.get("name")
		agreement_id = request.form.get("agreement_id")
		port = request.form.get("port")
		username = request.form.get("username")
		password = request.form.get("password")
		credence = Credence(name=name,
			agreement_id=agreement_id,
			port=port,
			username=username,
			password=password
			)
		db.session.add(credence)
		db.session.commit()
		flash('添加凭证成功.','warning')
	agreements = Agreement.query.all()
	return render_template('service/add_credence.html',agreements=agreements)

#删除凭证
@service_bp.route('/credence/<int:credence_id>/delete')
@login_required
@permission_required(Permission.backend_manage)
def delete_credence(credence_id):
	credence = Credence.query.get_or_404(credence_id)
	db.session.delete(credence)
	db.session.commit()
	flash('删除凭证成功.','warning')
	return redirect_back()


#修改凭证
@service_bp.route('/credence/<int:credence_id>/edit',methods=('GET','POST'))
@login_required
@permission_required(Permission.backend_manage)
def edit_credence(credence_id):
	credence = Credence.query.get_or_404(credence_id)
	if request.method == 'POST':
		credence.name = request.form.get("name")
		credence.agreement_id = request.form.get("agreement_id")
		credence.port = request.form.get("port")
		credence.username = request.form.get("username")
		credence.password = request.form.get("password")
		db.session.add(credence)
		db.session.commit()
		flash('修改凭证成功.','warning')
	credence = Credence.query.get_or_404(credence_id)
	agreements = Agreement.query.all()
	return render_template('service/edit_credence.html',credence=credence,agreements=agreements)


#公告
@service_bp.route('/notice/')
def notice():
	return render_template('service/notice.html')
#公告内容
@service_bp.route('/picchk/')
def picchk():
	return render_template('service/picchk.html')
