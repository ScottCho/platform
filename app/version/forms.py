from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
TextAreaField, HiddenField,SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

class BaselineForm(FlaskForm):
	versionno = StringField('SVN版本号(SIT)')
	sqlno = StringField('SQL序号',validators=[Length(0,20)])
	pckno = StringField('PCK序号')
	rollbackno = StringField('回滚脚本序号')
	mantisno = StringField('Mantis序号')
	content = TextAreaField('更新点',validators=[DataRequired()])
	mark = TextAreaField('备注')
	submit = SubmitField('更新基线')

	def validate_versionno(form,field):
		field = field.data
		if field!="" and not field.replace(',','').isdigit():
			raise ValidationError('请输入数字并以英文逗号分割.')

	def validate_sqlno(form,field):
		field = field.data
		if field!="" and not field.replace(',','').isdigit():
			raise ValidationError('请输入数字并以英文逗号分割.')

	def validate_pckno(form,field):
		field = field.data
		if field!="" and not field.replace(',','').isdigit():
			raise ValidationError('请输入数字并以英文逗号分割.')

	def validate_mantisno(form,field):
		field = field.data
		if field!="" and not field.replace(',','').isdigit():
			raise ValidationError('请输入数字并以英文逗号分割.')

	def validate_rollbackno(form,field):
		field = field.data
		if field!="" and not field.replace(',','').isdigit():
			raise ValidationError('请输入数字并以英文逗号分割.')


class SelectAppForm(FlaskForm):
	project = SelectField('项目',coerce=int)
	subsystem = SelectField('子系统',coerce=int)
	env = SelectField('环境',coerce=int)
	submit = SubmitField('下一步')


class SelectProjectForm(FlaskForm):
	project = SelectField('项目',coerce=int)
	submit = SubmitField('下一步')


class MergeBaselineForm(FlaskForm):
	date = StringField('更新包日期')
	baselineno = StringField('基线序号',validators=[DataRequired()])
	env = SelectField('合并环境',coerce=int)
	packageno  = StringField('今日发包次数')
	submit = SubmitField('下一步')

	def validate_blineno(form,field):
		field = field.data
		if field!="" and not field.replace(',','').isdigit():
			raise ValidationError('请输入数字并以英文逗号分割.')


class PackageForm(FlaskForm):
	name = StringField('名称')
	blineno = StringField('基线序号',validators=[DataRequired()])
	remark  = StringField('备注')
	project = StringField('项目')
	env = StringField('环境')
	submit = SubmitField('重新发布')

	def validate_blineno(form,field):
		field = field.data
		if field!="" and not field.replace(',','').isdigit():
			raise ValidationError('请输入数字并以英文逗号分割.')