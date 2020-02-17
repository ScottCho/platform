from flask import request, g
from flask_rest_jsonapi import (Api, ResourceDetail, ResourceList,
                                ResourceRelationship)


from app import db, flask_app
from app.apis.v2 import api
from app.models.version import Baseline, Blstatus, Package

from app.apis.v2.schemas.vcs import  BaselineSchema, BlstatusSchema, PackageSchema
from app.apis.v2.auth import auth_required

# Create resource managers
class BaselineList(ResourceList):
    decorators = auth_required,
    def after_create_object(self, obj, data, view_kwargs):
        print('*'*50)
        print(data)
        print(obj.content)
        print(str(request.args))

    def before_post(self, args, kwargs, data=None):
        print("""Hook to make custom work before post method""")
        data['developer_id'] = g.current_user.id
        print(data)

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