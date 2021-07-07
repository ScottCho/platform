# -*- coding: utf-8 -*-

from marshmallow_jsonapi.flask import Relationship, Schema
from marshmallow_jsonapi import fields


# Create logical data abstraction
# 项目
class ProjectSchema(Schema):
    class Meta:
        type_ = 'project'
        self_view = 'project_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'project_list'

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    zh_name = fields.Str(required=True)
    source_dir = fields.Str()
    target_dir = fields.Str()
    switch = fields.Bool()
    users = Relationship(self_view='project_users',
                         self_view_kwargs={'id': '<id>'},
                         related_view='user_list',
                         related_view_kwargs={'id': '<id>'},
                         many=True,
                         schema='UserSchema',
                         type_='user')
    apps = Relationship(self_view='project_apps',
                        self_view_kwargs={'id': '<id>'},
                        related_view='app_list',
                        related_view_kwargs={'id': '<id>'},
                        many=True,
                        schema='AppSchema',
                        type_='app')

    databases = Relationship(self_view='project_databases',
                             self_view_kwargs={'id': '<id>'},
                             related_view='database_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='DatabaseSchema',
                             type_='database')


# 用户
class UserSchema(Schema):
    class Meta:
        type_ = 'user'
        self_view = 'user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'user_list'

    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True)
    created = fields.DateTime()
    last_seen = fields.DateTime()
    confirmed = fields.Bool()
    active = fields.Bool()
    role_id = fields.Integer()
    role_name = fields.Function(lambda obj: "{}".format(obj.role.name))

    projects = Relationship(self_view='user_projects',
                            self_view_kwargs={'id': '<id>'},
                            related_view='project_list',
                            related_view_kwargs={'id': '<id>'},
                            many=True,
                            schema='ProjectSchema',
                            type_='project')
    role = Relationship(self_view='user_role',
                        self_view_kwargs={'id': '<id>'},
                        related_view='role_detail',
                        related_view_kwargs={'id': '<role_id>'},
                        schema='RoleSchema',
                        type_='role')


# 角色
class RoleSchema(Schema):
    class Meta:
        type_ = 'Role'
        self_view = 'role_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'role_list'

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    permissions = fields.Integer()
    default = fields.Integer()
    users = Relationship(self_view='role_users',
                         self_view_kwargs={'id': '<id>'},
                         related_view='user_list',
                         related_view_kwargs={'id': '<id>'},
                         many=True,
                         schema='UserSchema',
                         type_='user')
