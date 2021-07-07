# -*- coding: utf-8 -*-

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship


# Create logical data abstraction
class ServerSchema(Schema):
    class Meta:
        type_ = 'server'
        self_view = 'server_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'server_list'

    id = fields.Integer(dump_only=True)
    alias = fields.Str()
    hostname = fields.Str(required=True)
    ip = fields.Str(required=True)
    state = fields.Bool()
    os = fields.Str()
    remarks = fields.Str()
    credence_id = fields.Integer()
    credence_name = fields.Function(lambda obj: "{}".format(obj.credence.name))
    credence = Relationship(self_view='server_credence',
                            self_view_kwargs={'id': '<id>'},
                            related_view='credence_detail',
                            related_view_kwargs={'id': '<id>'},
                            schema='CredenceSchema',
                            type_='credence')

    groups = Relationship(self_view='server_groups',
                          self_view_kwargs={'id': '<id>'},
                          related_view='server_group_list',
                          related_view_kwargs={'id': '<id>'},
                          many=True,
                          schema='ServerGroupSchema',
                          type_='server_group')


# 机器分组
class ServerGroupSchema(Schema):
    class Meta:
        type_ = 'server_group'
        self_view = 'server_group_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'server_group_list'

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True, index=True)

    servers = Relationship(self_view='group_servers',
                           self_view_kwargs={'id': '<id>'},
                           related_view='server_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='ServerSchema',
                           type_='server')


# 协议
class CredenceSchema(Schema):
    class Meta:
        type_ = 'credence'
        self_view = 'credence_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'credence_list'

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    port = fields.Str(allow_none=True)
    username = fields.Str(allow_none=True)
    password = fields.Str(load_only=True, allow_none=True)
    ssh_key = fields.Str(allow_none=True)
    agreement_id = fields.Integer()
    agreement_name = fields.Function(
        lambda obj: "{}".format(obj.agreement.name))
    servers = Relationship(self_view='credence_servers',
                           self_view_kwargs={'id': '<id>'},
                           related_view='server_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='ServerSchema',
                           type_='server')
    agreement = Relationship(self_view='credence_agreement',
                             self_view_kwargs={'id': '<id>'},
                             related_view='agreement_detail',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='AgreementSchema',
                             type_='agreement')


# 登录协议
class AgreementSchema(Schema):
    class Meta:
        type_ = 'agreement'
        self_view = 'agreement_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'agreement_list'

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)

    credences = Relationship(self_view='agreement_credences',
                             self_view_kwargs={'id': '<id>'},
                             related_view='credence_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='CrendenceSchema',
                             type_='credence')


# 外部链接
class LinkSchema(Schema):
    class Meta:
        type_ = 'link'
        self_view = 'link_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'link_list'

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    category = fields.Str(allow_none=True)