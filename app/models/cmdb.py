from .. import db

#机器组和机器的连接表
machine_machinegroubs = db.Table('machine_ass_groub',
    db.Column('machine_id', db.Integer, db.ForeignKey('machines.id'), primary_key=True),
    db.Column('machinegroub_id', db.Integer, db.ForeignKey('machinegroubs.id'), primary_key=True)
)

#机器
class Machine(db.Model):
	__tablename__ = 'machines'
	id = db.Column(db.Integer, primary_key=True)
	alias = db.Column(db.String(80), nullable=False)
	hostname = db.Column(db.String(80), nullable=False)
	ip = db.Column(db.String(80), nullable=False)
	state = db.Column(db.Boolean, default=False)
	credence_id = db.Column(db.Integer,db.ForeignKey('credences.id'))
	os = db.Column(db.String(80))
	remarks =  db.Column(db.Text())
	credence = db.relationship('Credence',back_populates='machines')
	machinegroubs = db.relationship('MachineGroub',
		secondary=machine_machinegroubs,back_populates='machines'
		)
	def __repr__(self):
		return '<Machine.alias %r>' % self.alias

#凭证
class Credence(db.Model):
	__tablename__ = 'credences'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True,nullable=False)
	agreement_id = db.Column(db.Integer,db.ForeignKey('agreements.id'))
	port = db.Column(db.String(20),nullable=False)
	username = db.Column(db.String(80),nullable=False)
	password = db.Column(db.String(80))
	ssh_key = db.Column(db.Text)
	# agent_ip = db.Column(db.String(20))
	# agent_port = db.Column(db.String(10))
	# agent_password = db.Column(db.String(80))
	machines = db.relationship('Machine',back_populates='credence')
	def __repr__(self):
		return '<Credence.name %r>' % self.name

#登录协议
class Agreement(db.Model):
	__tablename__ = 'agreements'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	credences = db.relationship('Credence')
	def __repr__(self):
		return '<Agreement.name %r>' % self.name

#机器组
class MachineGroub(db.Model):
	__tablename__ = 'machinegroubs'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80),nullable=False)
	machines = db.relationship('Machine',
		secondary=machine_machinegroubs,back_populates='machinegroubs'
		)


