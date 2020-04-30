import logging

from flask import jsonify
from flask.views import MethodView
from flask_rest_jsonapi import ResourceList, ResourceRelationship
from app import db
from app.apis.v2 import api, api_v2
from app.apis.v2.auth import auth_required
from app.apis.v2.errors import api_abort
from app.apis.v2.schemas.service import (AppSchema, DatabaseSchema, EnvSchema,
                                         SchemaSchema, SubsystemSchema)
from app.models.service import App, Database, Env
from app.models.service import Schema as DBSchema
from app.models.service import Subsystem
from app.tasks import remote_shell

from . import BaseResourceDetail


# Create resource managers
class DatabaseList(ResourceList):
    decorators = (auth_required, )
    schema = DatabaseSchema
    data_layer = {'session': db.session, 'model': Database}


class DatabaseDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = DatabaseSchema
    data_layer = {'session': db.session, 'model': Database}


class DatabaseRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = DatabaseSchema
    data_layer = {'session': db.session, 'model': Database}


class SchemaList(ResourceList):
    decorators = (auth_required, )
    schema = SchemaSchema
    data_layer = {'session': db.session, 'model': DBSchema}


class SchemaDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = SchemaSchema
    data_layer = {'session': db.session, 'model': DBSchema}


class SchemaRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = SchemaSchema
    data_layer = {'session': db.session, 'model': DBSchema}


class EnvList(ResourceList):
    decorators = (auth_required, )
    schema = EnvSchema
    data_layer = {'session': db.session, 'model': Env}


class EnvDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = EnvSchema
    data_layer = {'session': db.session, 'model': Env}


class SubsystemList(ResourceList):
    decorators = (auth_required, )
    schema = SubsystemSchema
    data_layer = {'session': db.session, 'model': Subsystem}


class SubsystemDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = SubsystemSchema
    data_layer = {'session': db.session, 'model': Subsystem}


class AppList(ResourceList):
    decorators = (auth_required, )
    schema = AppSchema
    data_layer = {'session': db.session, 'model': App}


class AppDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = AppSchema
    data_layer = {'session': db.session, 'model': App}


class AppRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = AppSchema
    data_layer = {'session': db.session, 'model': App}


# 应用的重启和关闭
class AppManageAPI(MethodView):
    decorators = [auth_required]

    def get(self, action, app_id):
        app = App.query.get(app_id)
        if app is not None:
            env = app.env.name.lower()
            subsystem = app.subsystem.en_name.lower()
            username = app.credence.username
            password = app.credence.password
            ip = app.server.ip
            command = 'sh /usr/local/sbin/weblogic_{}.sh {} {}'.format(
                env, action, subsystem)
            print(command)
            try:
                result = remote_shell(ip,
                                      command,
                                      username=username,
                                      password=password)
            except Exception as e:
                return api_abort(400, str(e))
            else:
                return jsonify(data=[{'status': 200, 'detail': result}])
        else:
            return api_abort(404, 'app不存在')


# 数据库实例的重启和关闭
class DatabaseManageAPI(MethodView):
    decorators = [auth_required]

    def get(self, action, database_id):
        db = Database.query.get(database_id)
        if db is not None:
            username = db.credence.username
            password = db.credence.password
            instance = db.instance
            ip = db.server.ip
            command = 'sh /usr/local/sbin/restart_oracle.sh {} {}'.format(
                action, instance)
            logging.info('*' * 8 + 'execute command ' + command +
                         ' on oracle' + '@' + ip + '*' * 8)
            try:
                result = remote_shell(ip,
                                      command,
                                      username=username,
                                      password=password)
            except Exception as e:
                return api_abort(400, str(e))
            else:
                return jsonify(data=[{'status': 200, 'detail': result}])
        else:
            return api_abort(404, '数据库实例不存在')


# Create endpoints
api.route(DatabaseList, 'database_list', '/api/databases')
api.route(DatabaseDetail, 'database_detail', '/api/databases/<id>')
api.route(DatabaseRelationship, 'database_schemas',
          '/api/databases/<int:id>/relationships/schemas')
api.route(SchemaList, 'schema_list', '/api/schemas')
api.route(SchemaDetail, 'schema_detail', '/api/schemas/<int:id>')
api.route(SchemaRelationship, 'schema_database',
          '/api/schemas/<int:id>/relationships/databases')
api.route(EnvList, 'env_list', '/api/envs')
api.route(EnvDetail, 'env_detail', '/api/envs/<int:id>')
api.route(SubsystemList, 'subsystem_list', '/api/subsystems')
api.route(SubsystemDetail, 'subsystem_detail', '/api/subsystems/<int:id>')
api.route(AppList, 'app_list', '/api/apps')
api.route(AppDetail, 'app_detail', '/api/apps/<int:id>')
api.route(AppRelationship, 'app_project',
          '/api/apps/<int:id>/relationships/project')
api.route(AppRelationship, 'app_env', '/api/apps/<int:id>/relationships/env')
api.route(AppRelationship, 'app_subsystem',
          '/api/apps/<int:id>/relationships/subsystem')
api.route(AppRelationship, 'app_server',
          '/api/apps/<int:id>/relationships/server')
api.route(AppRelationship, 'app_schema',
          '/api/apps/<int:id>/relationships/schema')

# 重启应用端点
api_v2.add_url_rule('/apps/<action>/<int:app_id>',
                    view_func=AppManageAPI.as_view('app_manage'),
                    methods=[
                        'GET',
                    ])
#　数据库实例的重启和关闭端点
api_v2.add_url_rule('/databases/<action>/<int:database_id>',
                    view_func=DatabaseManageAPI.as_view('database_manage'),
                    methods=['GET', ]
                    )
