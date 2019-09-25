from flask import render_template,flash,redirect,url_for,request,current_app
from flask_login import login_required, current_user

from . import backstage_bp
from app.models.auth import User
from app import db
from app.utils.redirect_back import redirect_back
from ..models.auth import Permission,Role,Project
from app.decorators import admin_required, permission_required

#用户管理
@backstage_bp.route('/user/manage')
@login_required
@permission_required(Permission.backend_manage)
def manage_user():
	users = User.query.order_by(User.id.desc()).all()
	return render_template('backstage/manage_user.html',users=users)


#修改用户信息
@backstage_bp.route('/user/edit/<int:user_id>',methods=('POST','GET'))
@login_required
@permission_required(Permission.backend_manage)
def edit_user(user_id):
	user = User.query.get_or_404(user_id)
	roles = Role.query.all()
	if request.method == 'POST':
		user.username = request.form.get('username')
		user.email = request.form.get('email')
		user.phone = request.form.get('phone')
		user.role_id = request.form.get('role_id')
		if request.form.get('confirmed'):
			user.confirmed = 1
		else:
			user.confirmed = 0
		if request.form.get('active'):
			user.active = 1
		else:
			user.active = 0
		db.session.add(user)
		db.session.commit()
		flash('信息更新成功','success')
		return redirect_back()
	return render_template('backstage/edit_user.html',user=user, roles=roles)

# 禁用用户
@backstage_bp.route('/block/user/<int:user_id>')
@login_required
@permission_required(Permission.backend_manage)
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role.name in ['Administrator', 'Moderator']:
        flash('Permission denied.', 'warning')
    else:
        user.block()
        flash('Account blocked.', 'info')
    return redirect_back()

# 解禁用户
@backstage_bp.route('/unblock/user/<int:user_id>')
@login_required
@permission_required(Permission.backend_manage)
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unblock()
    flash('Block canceled.', 'info')
    return redirect_back()

#项目管理
@backstage_bp.route('/project/manage')
@login_required
@permission_required(Permission.backend_manage)
def manage_project():
	projects = Project.query.order_by(Project.id.desc()).all()
	return render_template('backstage/manage_project.html',projects=projects)

#新增项目
@backstage_bp.route('/project/new',methods=('GET','POST'))
@login_required
@permission_required(Permission.backend_manage)
def new_project():
	if request.method == 'POST':
		name = request.form.get('name')
		zh_name = request.form.get('zh_name')
		project = Project(name = name,
			zh_name = zh_name
			)
		db.session.add(project)
		db.session.commit()
		flash('添加项目成功.','success')
		return redirect_back()
	return render_template('backstage/new_project.html')

# 删除项目
@backstage_bp.route('/project/<int:project_id>')
@login_required
@permission_required(Permission.administer)
def delete_project(project_id):
	project = Project.query.get_or_404(project_id)
	db.session.delete(project)
	db.session.commit()
	flash('项目已经被删除','warning')
	return redirect_back()


#修改项目信息
@backstage_bp.route('/project/edit/<int:project_id>',methods=('POST','GET'))
@login_required
@permission_required(Permission.backend_manage)
def edit_project(project_id):
	project = Project.query.get_or_404(project_id)
	if request.method == 'POST':
		project.name = request.form.get('name')
		project.zh_name = request.form.get('zh_name')
		project.switch  = int(request.form.get('switch'))
		db.session.add(project)
		db.session.commit()
		flash('信息更新成功','success')
		return redirect_back()
	return render_template('backstage/edit_project.html',project=project)