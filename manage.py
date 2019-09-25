from app import flask_app
from flask_script import Manager, Shell
from flask_migrate import Migrate, upgrade, MigrateCommand
from app.models.auth import User,Role,Project
from app.models.service import Database,App
from app.models.welllink import Baseline,Blstatus
from app.models.machine import Agreement,Machine,Credence,MachineGroub
from app import db
from flask import current_app
import click


manager = Manager(flask_app)
migrate = Migrate(flask_app, db)


def make_shell_context():
   	return dict(app=flask_app, db=db, User=User, Project=Project,Baseline=Baseline,Database=Database,
    	Blstatus=Blstatus,Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@flask_app.cli.command()
def deploy():
    upgrade()
    Role.insert_roles()

if __name__ == '__main__':
    manager.run()
