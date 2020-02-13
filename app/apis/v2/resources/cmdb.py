from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship

from  app import flask_app
from app.models.cmdb import Machine, MachineGroub, Agreement, Credence
from app import db

from app.apis.v2 import api

# Create logical data abstraction
class MachineSchema(Schema):
    class Meta:
        type_ = 'machine'
        self_view = 'machine_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'machine_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    alias = fields.Str()
    hostname = fields.Str(required=True)
    ip = fields.Str(required=True)
    status = fields.Bool()
    os =  fields.Str()
    remarks = fields.Str()
    credence = Relationship(self_view='machine_credence',
                        self_view_kwargs={'id': '<id>'},
                        related_view='credence_detail',
                        related_view_kwargs={'id': '<id>'},
                        schema='CredenceSchema',
                        type_='credence')

class CredenceSchema(Schema):
    class Meta:
        type_ = 'credence'
        self_view = 'credence_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'credence_list'

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    port = fields.Str(required=True)
    username = fields.Str()
    password = fields.Str()
    ssh_key = fields.Str()
    machines = Relationship(self_view='credence_machines',
                           self_view_kwargs={'id': '<id>'},
                           related_view='machine_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='MachineSchema',
                           type_='machine')


# Create resource managers
class MachineList(ResourceList):
    schema = MachineSchema
    data_layer = {'session': db.session,
                  'model': Machine}

class MachineDetail(ResourceDetail):
    schema = MachineSchema
    data_layer = {'session': db.session,
                  'model': Machine}

class MachineRelationship(ResourceRelationship):
    schema = MachineSchema
    data_layer = {'session': db.session,
                  'model': Machine}

class CredenceList(ResourceList):
    schema = CredenceSchema
    data_layer = {'session': db.session,
                  'model': Credence}

class CredenceDetail(ResourceDetail):
    schema = CredenceSchema
    data_layer = {'session': db.session,
                  'model': Credence}

class CredenceRelationship(ResourceRelationship):
    schema = CredenceSchema
    data_layer = {'session': db.session,
                  'model': Credence}
       
# Create endpoints
api.route(MachineList, 'machine_list', '/api/machines')
api.route(MachineDetail, 'machine_detail', '/api/machines/<int:id>')
api.route(MachineRelationship, 'machine_credence', '/api/machines/<int:id>/relationships/credence')
api.route(CredenceList, 'credence_list', '/api/credences')
api.route(CredenceDetail, 'credence_detail', '/api/credences/<int:id>')
api.route(CredenceRelationship, 'credence_machines', '/api/credences/<int:id>/relationships/machines')
