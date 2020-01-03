from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship

from  app import flask_app
from app.models.service import Database, App, Env, Subsystem
from app.models.service import Schema as DBSchema
from app import db

from app.apis import api

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


# Create endpoints
api.route(DatabaseList, 'database_list', '/api/databases')
api.route(DatabaseDetail, 'database_detail', '/api/databases/<int:id>')
api.route(DatabaseRelationship, 'database_schemas', '/api/databases/<int:id>/relationships/schemas')
api.route(SchemaList, 'schema_list', '/api/schemas')
api.route(SchemaDetail, 'schema_detail', '/api/schemas/<int:id>')
api.route(SchemaRelationship, 'schema_database', '/api/schemas/<int:id>/relationships/databases')
