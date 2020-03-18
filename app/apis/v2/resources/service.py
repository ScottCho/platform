from flask import jsonify
from flask.views import MethodView, MethodViewType
from app.apis.v2 import api_v2
from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship


from  app import flask_app
from app.models.service import Database, App, Env, Subsystem
from app.models.service import Schema as DBSchema
from app import db

from app.apis.v2 import api
from app.apis.v2.schemas.service import DatabaseSchema, SchemaSchema, EnvSchema, SubsystemSchema, AppSchema
from app.apis.v2.auth import auth_required
from app.apis.v2.errors import api_abort
from app.apis.v2 import api_v2

from app.tasks import remote_shell

# Create resource managers
class DatabaseList(ResourceList):
    decorators = (auth_required,)
    schema = DatabaseSchema
    data_layer = {'session': db.session,
                  'model': Database}

class DatabaseDetail(ResourceDetail):
    decorators = (auth_required,)
    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id':id})
                self._data_layer.delete_object(obj, {'id':id})
    schema = DatabaseSchema
    data_layer = {'session': db.session,
                  'model': Database}

class DatabaseRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = DatabaseSchema
    data_layer = {'session': db.session,
                  'model': Database}

class SchemaList(ResourceList):
    decorators = (auth_required,)
    schema = SchemaSchema
    data_layer = {'session': db.session,
                  'model': DBSchema}

class SchemaDetail(ResourceDetail):
    decorators = (auth_required,)
        # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id':id})
                self._data_layer.delete_object(obj, {'id':id})

    schema = SchemaSchema
    data_layer = {'session': db.session,
                  'model': DBSchema}

class SchemaRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = SchemaSchema
    data_layer = {'session': db.session,
                  'model': DBSchema}

class EnvList(ResourceList):
    decorators = (auth_required,)
    schema = EnvSchema
    data_layer = {'session': db.session,
                  'model': Env}

class EnvDetail(ResourceDetail):
    decorators = (auth_required,)
    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id':id})
                self._data_layer.delete_object(obj, {'id':id})
    schema = EnvSchema
    data_layer = {'session': db.session,
                  'model': Env}

class SubsystemList(ResourceList):
    decorators = (auth_required,)
    schema = SubsystemSchema
    data_layer = {'session': db.session,
                  'model': Subsystem}

class SubsystemDetail(ResourceDetail):
    decorators = (auth_required,)
    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id':id})
                self._data_layer.delete_object(obj, {'id':id})
    schema = SubsystemSchema
    data_layer = {'session': db.session,
                  'model': Subsystem}

class AppList(ResourceList):
    decorators = (auth_required,)
    schema = AppSchema
    data_layer = {'session': db.session,
                  'model': App}

class AppDetail(ResourceDetail):
    decorators = (auth_required,)
    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id':id})
                self._data_layer.delete_object(obj, {'id':id})
    schema = AppSchema
    data_layer = {'session': db.session,
                  'model': App}

class AppRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = AppSchema
    data_layer = {'session': db.session,
                  'model': App}

# 应用的重启和关闭
class AppManageAPI(MethodView):
    decorators = [auth_required]
    def get(self, action, app_id):
        app = App.query.get(app_id)
        env = app.env.name.lower()
        subsystem = app.subsystem.en_name.lower()
        username = app.credence.username
        password = app.credence.password
        ip = app.machine.ip
        command='sh /usr/local/sbin/weblogic_{}.sh {} {}'.format(env,action,subsystem)
        if app is not None:
            result = remote_shell(ip,command,username=username,password=password)
            return jsonify(data=[{'status':200, 'detail':result}])
        else:
            return api_abort(404,'app不存在')

# 数据库实例的重启和关闭
class DatabaseManageAPI(MethodView):
    decorators = [auth_required]
    def get(self, action, database_id):
	    db = Database.query.get(database_id)
        username = db.credence.username
        password = db.credence.password
        instance = db.instance
        ip = app.machine.ip
        command='sh /usr/local/sbin/restart_oracle.sh {} {}'.format(action,instance)
	    logging.info('*'*8+'execute command ' + command + ' on oracle'+'@'+db.host+'*'*8)
        if db is not None:
            result = remote_shell(ip,command,username=username,password=password)
            return jsonify(data=[{'status':200, 'detail':result}])
        else:
            return api_abort(404,'数据库实例不存在')
	

# Create endpoints
api.route(DatabaseList, 'database_list', '/api/databases')
api.route(DatabaseDetail, 'database_detail', '/api/databases/<int:id>')
api.route(DatabaseRelationship, 'database_schemas', '/api/databases/<int:id>/relationships/schemas')
api.route(SchemaList, 'schema_list', '/api/schemas')
api.route(SchemaDetail, 'schema_detail', '/api/schemas/<int:id>')
api.route(SchemaRelationship, 'schema_database', '/api/schemas/<int:id>/relationships/databases')
api.route(EnvList, 'env_list', '/api/envs')
api.route(EnvDetail, 'env_detail', '/api/envs/<int:id>')
api.route(SubsystemList, 'subsystem_list', '/api/subsystems')
api.route(SubsystemDetail, 'subsystem_detail', '/api/subsystems/<int:id>')
api.route(AppList, 'app_list', '/api/apps')
api.route(AppDetail, 'app_detail', '/api/apps/<int:id>')
api.route(AppRelationship, 'app_project', '/api/apps/<int:id>/relationships/project')
api.route(AppRelationship, 'app_env', '/api/apps/<int:id>/relationships/env')
api.route(AppRelationship, 'app_subsystem', '/api/apps/<int:id>/relationships/subsystem')
api.route(AppRelationship, 'app_machine', '/api/apps/<int:id>/relationships/machine')
api.route(AppRelationship, 'app_schema', '/api/apps/<int:id>/relationships/schema')

# 重启应用端点
api_v2.add_url_rule('/apps/<action>/<int:app_id>', view_func=AppManageAPI.as_view('app_manage'), methods=['GET',])
#　数据库实例的重启和关闭端点
api_v2.add_url_rule('/databases/<action>/<int:database_id>', view_func=DatabaseManageAPI.as_view('database_manage'), methods=['GET',])
