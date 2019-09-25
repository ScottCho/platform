#!/usr/bin/python
#-*- coding: UTF-8 -*-
from flask import render_template, redirect, request, url_for, flash
import logging
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth_bp
from .. import db

from ..models.auth import User,Project,Role
from ..localemail import send_email
from .forms import LoginForm,RegistrationForm,PasswordResetForm,PasswordResetRequestForm,\
ChangePasswordForm,ChangeEmailForm
from app.utils.redirect_back import redirect_back

'''
每次请求之前，如果当前用户已登录，账户未确认，请求端点不在认证蓝图；
将会被重定向到未认证视图函数
ping函数会更新用户的访问的时间
'''
@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

'''
未确认账户
'''
@auth_bp.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('index'))
    return render_template('auth/unconfirmed.html')

'''
重发确认账户确认邮件
'''
@auth_bp.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email([current_user.email], '确认您的登录账户',
               'mail/auth/confirm.html', user=current_user, token=token)
    flash('一封新的邮件已经发送到您的邮箱.','warning')
    return redirect(url_for('index'))



'''
登录
login_user() 函数的参数是要登录的用户，以及可选的“记住我”布尔值,当True时，会在浏览器中写入一个cookie 
Flask-Login会把原地址保存在查询字符串的next参数中，这个参数可从request.args 字典中读取。
'''

#登录用户
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('登录成功', 'success')
                return redirect_back()
            else:
                flash('您的账户被封禁', 'warning')
        flash('用户名或密码错误.','danger')
    return render_template('auth/login.html', form=form)



'''
注册视图
字段有：id,email,username,password,role_id,created
密码会被加密存储到数据库中
'''

#注册用户
@auth_bp.route('/register',methods=('GET','POST'))
def register():
    form = RegistrationForm()
    form.role_id.choices = [(g.id, g.name) for g in Role.query.filter(~Role.name.in_(['Moderator','Administrator'])).order_by('name')]
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    role_id=form.role_id.data
                    )
        db.session.add(user)
        db.session.commit() 
        token = user.generate_confirmation_token()
        send_email([user.email],'确认您的账户',
            'mail/auth/confirm.html',user=user,token=token)
        flash('一封确认邮件已经发送到您的邮箱.','info')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

'''
处理确认用户
'''
@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('您以经确认了账户. 谢谢!','success')
    else:
        flash('确认链接无效或者过期.','danger')
    return redirect(url_for('index'))



#处理重置密码请求
@auth_bp.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email([user.email], '运维平台-重置密码',
                       'mail/auth/reset_password.html',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('一封确认邮件已经发送到您的邮箱.','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/forget_password.html', form=form)

#重置密码
@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('您的密码已经重置.','info')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('index'))
    return render_template('auth/reset_password.html', form=form)

#修改密码   
@auth_bp.route('/change/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('更新密码成功.','success')
            return redirect(url_for('index'))
        else:
            flash('无效密码.','danger')
    return render_template("auth/change_password.html", form=form)

'''
修改邮箱
'''
#处理修改邮箱请求
@auth_bp.route('/change/email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email([new_email], '确认您的账户',
                       'mail/auth/change_email.html',
                       user=current_user, token=token)
            flash('一封确认邮件已经发送到您的邮箱..','info')
            return redirect(url_for('index'))
        else:
            flash('无效的邮箱或密码.','danger')
    return render_template("auth/change_email.html", form=form)


@auth_bp.route('/change/email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('您的邮箱地址已经更新.','success')
    else:
        flash('无效请求.','danger')
    return redirect(url_for('index'))

'''
退出登录
'''

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经退出登录.','info')
    return redirect_back()


'''
用户加入项目
'''
@auth_bp.route('/join/project', methods=['GET', 'POST'])
@login_required
def join_project():
    if request.method == 'POST':
        proj_name = request.form.get('proj_name')
        project = Project.query.filter_by(name=proj_name).first()
        current_user.projects.append(project)
        db.session.add(current_user)
        db.session.commit()
        flash('您已经加入项目'+proj_name,'info')
        return redirect(url_for('index'))
    all_projects = Project.query.all()
    joined_projects = current_user.projects
    unjoin_projects = [i for i in all_projects if i not in joined_projects]
    return render_template('auth/join_project.html',projects = unjoin_projects)

'''
用户退出项目
'''
@auth_bp.route('/exit/project', methods=['GET', 'POST'])
@login_required
def exit_project():
    if request.method == 'POST':
        proj_name = request.form.get('proj_name')
        project = Project.query.filter_by(name=proj_name).first()
        current_user.projects.remove(project)
        db.session.add(current_user)
        db.session.commit()
        flash('您已经退出项目'+proj_name,'info')
        return redirect(url_for('index'))
    return render_template('auth/exit_project.html',projects = current_user.projects)


'''
用户视图
'''
@auth_bp.route('/user/<email>')
@login_required
def user(email):
    user = User.query.filter_by(email=email).first_or_404()
    return render_template('auth/user.html',user=user)