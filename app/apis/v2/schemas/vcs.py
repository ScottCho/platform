# -*- coding: utf-8 -*-

from marshmallow_jsonapi.flask import Relationship, Schema
from marshmallow_jsonapi import fields

# Create logical data abstraction
class BaselineSchema(Schema):
    class Meta:
        type_ = 'baseline'
        self_view = 'baseline_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'baseline_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    content = fields.Str()
    sqlno = fields.Str()
    pckno = fields.Str()
    rollbackno = fields.Str()
    created = fields.Str()
    updateno = fields.Str()
    mantisno = fields.Str()
    jenkins_last_build = fields.Boolean()
    jenkins_build_number = fields.Integer()
    versionno = fields.Str()
    mark = fields.Str()
    app_id = fields.Integer()
    package_id = fields.Integer()
    developer_id = fields.Integer()
    status_id = fields.Integer()
    status_name = fields.Function(lambda obj: "{}".format(obj.status.status))
    package_name = fields.Function(lambda obj: "{}".format(obj.package.name))
    app_name = fields.Function(lambda obj: "{}-{}-{}".format(obj.app.project.name.lower(),obj.app.env.name.lower(),obj.app.subsystem.en_name.lower()))
    developer_username = fields.Function(lambda obj: "{}".format(obj.developer.username))
    developer = Relationship(self_view='baseline_developer',
                             self_view_kwargs={'id': '<id>'},
                             related_view='user_detail',
                             related_view_kwargs={'id': '<developer_id>'},
                             schema='UserSchema',
                             type_='user')
    app = Relationship(self_view='baseline_app',
                             self_view_kwargs={'id': '<id>'},
                             related_view='app_detail',
                             related_view_kwargs={'id': '<app_id>'},
                             schema='AppSchema',
                             type_='app')
    status = Relationship(self_view='baseline_status',
                             self_view_kwargs={'id': '<id>'},
                             related_view='blstatus_detail',
                             related_view_kwargs={'id': '<status_id>'},
                             schema='BlstatusSchema',
                             type_='blstatus')      
    package = Relationship(self_view='baseline_package',
                             self_view_kwargs={'id': '<id>'},
                             related_view='package_detail',
                             related_view_kwargs={'id': '<package_id>'},
                             schema='PackageSchema',
                             type_='package')     
  

class BlstatusSchema(Schema):
    class Meta:
        type_ = 'blstatus'
        self_view = 'blstatus_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'blstatus_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    status = fields.Str(required=True)

class PackageSchema(Schema):
    class Meta:
        type_ = 'package'
        self_view = 'package_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'package_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    rlsdate = fields.Str()
    blineno = fields.Str()
    merge_blineno = fields.Str()
    remark = fields.Str()
    project_id = fields.Integer()
    env_id = fields.Integer()
    package_count = fields.Str()
    project_name = fields.Function(lambda obj: "{}".format(obj.project.name))
    env_name = fields.Function(lambda obj: "{}".format(obj.env.name))
    project = Relationship(self_view='package_project',
                             self_view_kwargs={'id': '<id>'},
                             related_view='project_detail',
                             related_view_kwargs={'id': '<project_id>'},
                             schema='ProjectSchema',
                             type_='project') 
    env = Relationship(self_view='package_env',
                             self_view_kwargs={'id': '<id>'},
                             related_view='env_detail',
                             related_view_kwargs={'id': '<env_id>'},
                             schema='EnvSchema',
                             type_='env') 
    baselines= Relationship(self_view='package_baselines',
                             self_view_kwargs={'id': '<id>'},
                             related_view='baseline_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='BaselineSchema',
                             type_='baseline')