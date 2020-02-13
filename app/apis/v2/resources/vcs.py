from flask import request
from flask_rest_jsonapi import (Api, ResourceDetail, ResourceList,
                                ResourceRelationship)
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app import db, flask_app
from app.apis.v2 import api
from app.models.version import Baseline, Blstatus, Package


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
   
     

# Create resource managers
class BaselineList(ResourceList):

    def after_create_object(self, obj, data, view_kwargs):
        print('*'*50)
        print(data)
        print(obj.content)
        print(str(request.args))


    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline,
                  'methods': {'after_create_object': after_create_object}}

class BaselineDetail(ResourceDetail):
    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline}

class BaselineRelationship(ResourceRelationship):
    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline}

class BlstatusList(ResourceList):
    schema = BlstatusSchema
    data_layer = {'session': db.session,
                  'model': Blstatus}

class BlstatusDetail(ResourceDetail):
    schema = BlstatusSchema
    data_layer = {'session': db.session,
                  'model': Blstatus}

#更新包
class PackageList(ResourceList):
    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageDetail(ResourceDetail):
    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageRelationship(ResourceRelationship):
    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}   

# Create endpoints
#基线
api.route(BaselineList, 'baseline_list', '/api/baselines')
api.route(BaselineDetail, 'baseline_detail', '/api/baselines/<int:id>')
api.route(BaselineRelationship, 'baseline_developer', '/api/baselines/<int:id>/relationships/developer')
api.route(BaselineRelationship, 'baseline_app', '/api/baselines/<int:id>/relationships/app')
api.route(BaselineRelationship, 'baseline_status', '/api/baselines/<int:id>/relationships/status')
api.route(BaselineRelationship, 'baseline_package', '/api/baselines/<int:id>/relationships/package')
#基线状态
api.route(BlstatusList, 'blstatus_list', '/api/blstatus')
api.route(BlstatusDetail, 'blstatus_detail', '/api/blstatus/<int:id>')
#更新包
api.route(PackageList, 'package_list', '/api/packages')
api.route(PackageDetail, 'package_detail', '/api/packages/<int:id>')
api.route(PackageRelationship, 'package_project', '/api/packages/<int:id>/relationships/project')
api.route(PackageRelationship, 'package_env', '/api/packages/<int:id>/relationships/env')
api.route(PackageRelationship, 'package_baselines', '/api/packages/<int:id>/relationships/baselines')