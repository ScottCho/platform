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
    state = fields.Bool()
    os =  fields.Str()
    remarks = fields.Str()
    credence_id = fields.Integer()
    credence_name = fields.Function(lambda obj: "{}".format(obj.credence.name))
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
    port = fields.Str(allow_none=True)
    username = fields.Str(allow_none=True)
    password = fields.Str(allow_none=True)
    ssh_key = fields.Str(allow_none=True)
    agreement_id = fields.Integer()
    agreement_name = fields.Function(lambda obj: "{}".format(obj.agreement.name))
    machines = Relationship(self_view='credence_machines',
                           self_view_kwargs={'id': '<id>'},
                           related_view='machine_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='MachineSchema',
                           type_='machine')
    agreement = Relationship(self_view='credence_agreement',
                           self_view_kwargs={'id': '<id>'},
                           related_view='agreement_detail',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='AgreementSchema',
                           type_='agreement')

class AgreementSchema(Schema):
    class Meta:
        type_ = 'agreement'
        self_view = 'agreement_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'agreement_list'

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)

    credences = Relationship(self_view='agreement_credences',
                           self_view_kwargs={'id': '<id>'},
                           related_view='credence_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='CrendenceSchema',
                           type_='credence')