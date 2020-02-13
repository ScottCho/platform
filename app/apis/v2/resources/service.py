from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship

from  app import flask_app
from app.models.service import Database, App, Env, Subsystem
from app.models.service import Schema as DBSchema
from app import db

from app.apis.v2 import api

# Create logical data abstraction
class DatabaseSchema(Schema):
    class Meta:
        type_ = 'database'
        self_view = 'database_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'database_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    instance = fields.Str(required=True)
    port = fields.Str()
    mark = fields.Str()
    schemas = Relationship(self_view='database_schemas',
                             self_view_kwargs={'id': '<id>'},
                             related_view='schema_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='SchemaSchema',
                             type_='schema')

class SchemaSchema(Schema):
    class Meta:
        type_ = 'schema'
        self_view = 'schema_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'schema_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(load_only=True)
    instance = Relationship(self_view='schema_database',
                             self_view_kwargs={'id': '<id>'},
                             related_view='database_detail',
                             related_view_kwargs={'id': '<id>'},
                             schema='DatabaseSchema',
                             type_='database')


class EnvSchema(Schema):
    class Meta:
        type_ = 'env'
        self_view = 'env_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'env_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    # apps = Relationship(self_view='app_schemas',
    #                          self_view_kwargs={'id': '<id>'},
    #                          related_view='schema_list',
    #                          related_view_kwargs={'id': '<id>'},
    #                          many=True,
    #                          schema='SchemaSchema',
    #                          type_='schema')

class SubsystemSchema(Schema):
    class Meta:
        type_ = 'subsystem'
        self_view = 'subsystem_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'subsystem_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    en_name = fields.Str(required=True)
    zh_name = fields.Str(required=True)

class AppSchema(Schema):
    class Meta:
        type_ = 'app'
        self_view = 'app_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'app_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    log_dir = fields.Str()
    jenkins_job_dir = fields.Str()
    source_dir = fields.Str()
    project_id = fields.Integer()
    machine_id = fields.Integer()
    schema_id = fields.Integer()
    subsystem_id = fields.Integer()
    #, obj.env.name.upper(),obj.subsystem.name.upper()
    display_name = fields.Function(lambda obj: "{}-{}-{}".format(obj.project.name.lower(),obj.env.name.lower(),obj.subsystem.en_name.lower()))

    machine = Relationship(self_view='app_machine',
                             self_view_kwargs={'id': '<id>'},
                             related_view='machine_detail',
                             related_view_kwargs={'id': '<machine_id>'},
                             schema='MachineSchema',
                             type_='machine') 
    project = Relationship(self_view='app_project',
                             self_view_kwargs={'id': '<id>'},
                             related_view='project_detail',
                             related_view_kwargs={'id': '<project_id>'},
                             schema='ProjectSchema',
                             type_='project')   
    env = Relationship(self_view='app_env',
                             self_view_kwargs={'id': '<id>'},
                             related_view='env_detail',
                             related_view_kwargs={'id': '<env_id>'},
                             schema='EnvSchema',
                             type_='env')
    subsystem = Relationship(self_view='app_subsystem',
                             self_view_kwargs={'id': '<id>'},
                             related_view='subsystem_detail',
                             related_view_kwargs={'id': '<subsystem_id>'},
                             schema='SubsystemSchema',
                             type_='subsystem')
    schema = Relationship(self_view='app_schema',
                             self_view_kwargs={'id': '<id>'},
                             related_view='schema_detail',
                             related_view_kwargs={'id': '<schema_id>'},
                             schema='SchemaSchema',
                             type_='schema')

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
                  'model': Schema}

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
api.route(SchemaList, 'subsystem_list', '/api/subsystems')
api.route(SchemaDetail, 'subsystem_detail', '/api/subsystems/<int:id>')
api.route(AppList, 'app_list', '/api/apps')
api.route(AppDetail, 'app_detail', '/api/apps/<int:id>')
api.route(AppRelationship, 'app_project', '/api/apps/<int:id>/relationships/project')
api.route(AppRelationship, 'app_env', '/api/apps/<int:id>/relationships/env')
api.route(AppRelationship, 'app_subsystem', '/api/apps/<int:id>/relationships/subsystem')
api.route(AppRelationship, 'app_machine', '/api/apps/<int:id>/relationships/machine')
api.route(AppRelationship, 'app_schema', '/api/apps/<int:id>/relationships/schema')