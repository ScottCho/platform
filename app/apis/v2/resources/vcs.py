import os

from flask import request, g
from flask_rest_jsonapi import (Api, ResourceDetail, ResourceList,
                                ResourceRelationship)

from werkzeug.wrappers import Response
from flask import request, url_for, make_response
from flask.wrappers import Response as FlaskResponse
from flask.views import MethodView, MethodViewType
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from marshmallow import ValidationError

from flask_rest_jsonapi.querystring import QueryStringManager as QSManager
from flask_rest_jsonapi.pagination import add_pagination_links
from flask_rest_jsonapi.exceptions import InvalidType, BadRequest, RelationNotFound
from flask_rest_jsonapi.decorators import check_headers, check_method_requirements, jsonapi_exception_formatter
from flask_rest_jsonapi.schema import compute_schema, get_relationships, get_model_field
from flask_rest_jsonapi.data_layers.base import BaseDataLayer
from flask_rest_jsonapi.data_layers.alchemy import SqlalchemyDataLayer
from flask_rest_jsonapi.utils import JSONEncoder

from app import db, flask_app
from app.apis.v2 import api
from app.models.version import Baseline, Blstatus, Package

from app.apis.v2.schemas.vcs import  BaselineSchema, BlstatusSchema, PackageSchema
from app.apis.v2.auth import auth_required
from app.utils import execute_cmd, fnmatch_file, switch_char
from app.localemail import send_email

# Create resource managers
class BaselineList(ResourceList):
    decorators = (auth_required,)
    
    #　处理基线的默认内容
    def before_post(self, args, kwargs, data=None):
        """Hook to make custom work before post method"""
        data['developer_id'] = g.current_user.id
        data['updateno'] = 1
        data['status_id'] =5

    def after_post(self, result):
        """Hook to make custom work after post method"""
        id = int(result['data']['id'])
        obj = self._data_layer.get_object({'id':id})
        message = obj.update_baseline()
        # 发送邮件
        obj.baseline_email()
        # 更新结果返回
        result.update({'detail': message})
        return result

    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline
                }

class BaselineDetail(ResourceDetail):
    decorators = (auth_required,)
    def before_patch(self, args, kwargs, data=None):
        """Hook to make custom work before patch method"""
        obj = Baseline.query.get_or_404(kwargs['id'])
        data['updateno'] = obj.updateno+1
    
    def after_patch(self, result):
        """Hook to make custom work after patch method"""
        id = int(result['data']['id'])
        obj = self._data_layer.get_object({'id':id})
        message = obj.update_baseline()
        # 发送邮件
        obj.baseline_email()
        # 更新结果返回
        result.update({'detail': message})
        return result

    # 改写成批量删除，kwargs={'id':'[1,2,3]'}
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        for id in ids[1:-1].split(','):
            obj = self._data_layer.get_object({'id':id})
            self._data_layer.delete_object(obj, {'id':id})

    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline  
                }

class BaselineRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline}

class BlstatusList(ResourceList):
    decorators = (auth_required,)
    schema = BlstatusSchema
    data_layer = {'session': db.session,
                  'model': Blstatus}

class BlstatusDetail(ResourceDetail):
    decorators = (auth_required,)
    schema = BlstatusSchema
    data_layer = {'session': db.session,
                  'model': Blstatus}

#更新包
class PackageList(ResourceList):
    decorators = (auth_required,)
    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageDetail(ResourceDetail):
    decorators = (auth_required,)
    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}   

# Create endpoints
#基线
api.route(BaselineList, 'baseline_list', '/api/baselines')
api.route(BaselineDetail, 'baseline_detail', '/api/baselines/<id>')
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