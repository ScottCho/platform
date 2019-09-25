from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models.auth import User, Role


class RegistrationForm(FlaskForm):
	email = StringField('公司邮箱', validators=[DataRequired(), Length(1, 64),
											 Email()],
											render_kw={'placeholder': 'Email','class':"form-control",'value':'@sinosoft.com.cn'})
	username = StringField('用户名', validators=[
		DataRequired(), Length(1, 64)], render_kw={'placeholder': '真实中文名','class':"form-control"})
	role_id = SelectField('角色', coerce=int,render_kw={'class':"form-control"})
	password = PasswordField('密码', validators=[
		DataRequired(), EqualTo('password2', message='密码不一致.')],
		render_kw={'placeholder': 'password','class':"form-control"})
	password2 = PasswordField('确认密码', validators=[DataRequired()],
		render_kw={'placeholder': 'Retype password','class':"form-control"})
	submit = SubmitField('注册',render_kw={'class':'btn btn-lg btn-primary btn-block'})

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('邮箱已被注册.')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('用户已被注册.')

class LoginForm(FlaskForm):
	email = StringField('公司邮箱', validators=[DataRequired(), Length(1, 64),Email()],
		render_kw={'class':"form-control",'placeholder':'Email address','autofocus':True})
	password = PasswordField('密码', validators=[DataRequired()],
		render_kw={'class':"form-control",'placeholder':'Password'})
	remember_me = BooleanField('记住我',render_kw={'type':'checkbox','value':'True'})
	submit = SubmitField('登录',render_kw={'class':'btn btn-lg btn-primary btn-block'})

class ChangePasswordForm(FlaskForm):
	old_password = PasswordField('旧密码', validators=[DataRequired()],
		render_kw={'placeholder': 'password','class':"form-control"})
	password = PasswordField('新密码', validators=[
		DataRequired(), EqualTo('password2', message='Passwords must match.')],
		render_kw={'placeholder': 'password','class':"form-control"})
	password2 = PasswordField('确认新密码',
							  validators=[DataRequired()],
		render_kw={'placeholder': 'password','class':"form-control"})
	submit = SubmitField('更新密码', render_kw={'class':"btn btn-lg btn-primary btn-block"})

class ChangeEmailForm(FlaskForm):
	email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64),Email()],
		render_kw={'placeholder': 'Email','class':"form-control",'value':'@sinosoft.com.cn'})
	password = PasswordField('密码', validators=[DataRequired()],
		render_kw={'placeholder': 'password','class':"form-control"})
	submit = SubmitField('更新邮箱',render_kw={'class':"btn btn-lg btn-primary btn-block"})

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('邮箱已被注册.')

class PasswordResetRequestForm(FlaskForm):
	email = StringField('请输入注册邮箱', validators=[DataRequired(), Length(1, 64),Email()],
		render_kw={'placeholder': 'Email','class':"form-control",'value':'@sinosoft.com.cn','autofocus':True})
	submit = SubmitField('提交',render_kw={'class':"btn btn-lg btn-primary btn-block"})


class PasswordResetForm(FlaskForm):
	password = PasswordField('新密码', validators=[
		DataRequired(), EqualTo('password2', message='Passwords must match')],
		render_kw={'placeholder': 'password','class':"form-control"})
	password2 = PasswordField('确认密码', validators=[DataRequired()],
		render_kw={'placeholder': 'password','class':"form-control"})
	submit = SubmitField('重置密码',render_kw={'class':"btn btn-primary btn-block btn-flat"})