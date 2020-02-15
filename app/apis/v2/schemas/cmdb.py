# -*- coding: utf-8 -*-
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

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
    credence_id = fields.Integer()
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