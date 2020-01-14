from .. import db


#数据库实例
class Database(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	instance = db.Column(db.String(80),nullable=False)
	port = db.Column(db.String(32),nullable=False)
	project = db.Column(db.String(80),nullable=False)
	project_id = db.Column(db.Integer,db.ForeignKey('projects.id'))
	mark = db.Column(db.String(80))
	project = db.relationship('Project')
	schemas = db.relationship('Schema',back_populates='instance')
	credence_id = db.Column(db.Integer,db.ForeignKey('credences.id'))
	credence = db.relationship('Credence')
	machine_id = db.Column(db.Integer,db.ForeignKey('machines.id'))
	machine = db.relationship('Machine')

#数据库的Schema
class Schema(db.Model):
	__tablename__ = 'db_schemas'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128),nullable=False)
	password = db.Column(db.String(80),nullable=False)
	instance_id = db.Column(db.Integer,db.ForeignKey('database.id'))
	app = db.relationship('App',uselist=False) #建立与APP一对一的关系
	instance = db.relationship('Database',back_populates='schemas')

class App(db.Model):
    __tablename__ = 'apps'
    id = db.Column(db.Integer, primary_key=True)
    log_dir = db.Column(db.String(80),nullable=False)
    jenkins_job_dir = db.Column(db.String(256))
    source_dir = db.Column(db.String(256))
    project_id = db.Column(db.Integer,db.ForeignKey('projects.id'))
    project = db.relationship('Project',back_populates='apps')
    env_id = db.Column(db.Integer,db.ForeignKey('envs.id'))
    env = db.relationship('Env',back_populates='apps')
    subsystem_id = db.Column(db.Integer,db.ForeignKey('subsystems.id'))
    subsystem = db.relationship('Subsystem')
    baselines = db.relationship('app.models.version.Baseline',back_populates='app')
    machine_id = db.Column(db.Integer,db.ForeignKey('machines.id'))
    machine = db.relationship('Machine')
    schema_id = db.Column(db.Integer,db.ForeignKey('db_schemas.id'))
    schema = db.relationship('Schema')

class Subsystem(db.Model):
	__tablename__ = 'subsystems'
	id = db.Column(db.Integer,primary_key=True)
	en_name = db.Column(db.String(32),nullable=False)
	zh_name = db.Column(db.String(32),nullable=False)


class Env(db.Model):
	__tablename__ = 'envs'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(16),nullable=False)
	apps = db.relationship('App',back_populates='env')
	packages = db.relationship('Package',back_populates='env')