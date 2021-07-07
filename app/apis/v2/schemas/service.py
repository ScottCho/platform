# -*- coding: utf-8 -*-

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship


# Create logical data abstraction
class DatabaseSchema(Schema):
    class Meta:
        type_ = 'database'
        self_view = 'database_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'database_list'

    id = fields.Integer(dump_only=True)
    instance = fields.Str(required=True)
    port = fields.Str()
    mark = fields.Str(allow_none=True)
    credence_id = fields.Integer()
    server_id = fields.Integer()
    project_id = fields.Integer()
    project_name = fields.Function(lambda obj: "{}".format(obj.project.name))
    server_hostname = fields.Function(
        lambda obj: "{}".format(obj.server.hostname))
    schemas = Relationship(self_view='database_schemas',
                           self_view_kwargs={'id': '<id>'},
                           related_view='schema_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='SchemaSchema',
                           type_='schema')

    project = Relationship(self_view='database_project',
                           self_view_kwargs={'id': '<id>'},
                           related_view='project_detail',
                           related_view_kwargs={'id': '<project_id>'},
                           schema='ProjectSchema',
                           type_='project')

class SchemaSchema(Schema):
    class Meta:
        type_ = 'schema'
        self_view = 'schema_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'schema_list'

    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(load_only=True)
    instance_id = fields.Integer()
    instance_name = fields.Function(
        lambda obj: "{}".format(obj.instance.instance))
    hostname = fields.Function(
        lambda obj: "{}".format(obj.instance.server.hostname))
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

    id = fields.Integer(dump_only=True)
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

    id = fields.Integer(dump_only=True)
    en_name = fields.Str(required=True)
    zh_name = fields.Str(required=True)


class AppSchema(Schema):
    class Meta:
        type_ = 'app'
        self_view = 'app_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'app_list'

    id = fields.Integer(dump_only=True)
    log_dir = fields.Str()
    jenkins_job_dir = fields.Str()
    port = fields.Str()
    deploy_dir = fields.Str(allow_none=True)
    jenkins_job_name = fields.Str(allow_none=True)
    alias = fields.Str()
    context = fields.Str(allow_none=True)
    service_url = fields.Function(lambda obj: "http://{}:{}/{}".format(
        obj.server.ip, obj.port, obj.context))
    source_dir = fields.Str()
    project_id = fields.Integer()
    server_id = fields.Integer()
    schema_id = fields.Integer()
    subsystem_id = fields.Integer()
    credence_id = fields.Integer()
    credence_name = fields.Function(lambda obj: "{}".format(obj.credence.name))
    env_id = fields.Integer()
    name = fields.Str()
    project_name = fields.Function(lambda obj: "{}".format(obj.project.name))
    subsystem_name = fields.Function(
        lambda obj: "{}".format(obj.subsystem.en_name))
    env_name = fields.Function(lambda obj: "{}".format(obj.env.name))
    server_hostname = fields.Function(
        lambda obj: "{}".format(obj.server.hostname))

    server = Relationship(self_view='app_server',
                          self_view_kwargs={'id': '<id>'},
                          related_view='server_detail',
                          related_view_kwargs={'id': '<server_id>'},
                          schema='serverSchema',
                          type_='server')
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
