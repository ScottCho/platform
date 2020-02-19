from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship


from  app import flask_app
from app.models.service import Database, App, Env, Subsystem
from app.models.service import Schema as DBSchema
from app import db

from app.apis.v2 import api
from app.apis.v2.schemas.service import DatabaseSchema, SchemaSchema, EnvSchema, SubsystemSchema, AppSchema


# Create resource managers
class DatabaseList(ResourceList):
    schema = DatabaseSchema
    data_layer = {'session': db.session,
                  'model': Database}

class DatabaseDetail(ResourceDetail):
    schema = DatabaseSchema
    data_layer = {'session': db.session,
                  'model': Database}

class DatabaseRelationship(ResourceRelationship):
    schema = DatabaseSchema
    data_layer = {'session': db.session,
                  'model': Database}

class SchemaList(ResourceList):
    schema = SchemaSchema
    data_layer = {'session': db.session,
                  'model': DBSchema}

class SchemaDetail(ResourceDetail):
    schema = SchemaSchema
    data_layer = {'session': db.session,
                  'model': DBSchema}

class SchemaRelationship(ResourceRelationship):
    schema = SchemaSchema
    data_layer = {'session': db.session,
                  'model': DBSchema}

class EnvList(ResourceList):
    schema = EnvSchema
    data_layer = {'session': db.session,
                  'model': Env}

class EnvDetail(ResourceDetail):
    schema = EnvSchema
    data_layer = {'session': db.session,
                  'model': Env}

class SubsystemList(ResourceList):
    schema = SubsystemSchema
    data_layer = {'session': db.session,
                  'model': Subsystem}

class SubsystemDetail(ResourceDetail):
    schema = SubsystemSchema
    data_layer = {'session': db.session,
                  'model': Subsystem}

class AppList(ResourceList):
    schema = AppSchema
    data_layer = {'session': db.session,
                  'model': App}

class AppDetail(ResourceDetail):
    schema = AppSchema
    data_layer = {'session': db.session,
                  'model': App}

class AppRelationship(ResourceRelationship):
    schema = AppSchema
    data_layer = {'session': db.session,
                  'model': App}

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