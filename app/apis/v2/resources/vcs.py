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

    def post(self, *args, **kwargs):
        """Create an object"""
        json_data = request.get_json() or {}

        qs = QSManager(request.args, self.schema)

        schema = compute_schema(self.schema,
                                getattr(self, 'post_schema_kwargs', dict()),
                                qs,
                                qs.include)

        try:
            data, errors = schema.load(json_data)
        except IncorrectTypeError as e:
            errors = e.messages
            for error in errors['errors']:
                error['status'] = '409'
                error['title'] = "Incorrect type"
            return errors, 409
        except ValidationError as e:
            errors = e.messages
            for message in errors['errors']:
                message['status'] = '422'
                message['title'] = "Validation error"
            return errors, 422

        if errors:
            for error in errors['errors']:
                error['status'] = "422"
                error['title'] = "Validation error"
            return errors, 422

        self.before_post(args, kwargs, data=data)

        obj = self.create_object(data, kwargs)

        message = ''
        #更新应用程序
        if obj.versionno:
            message += obj.build_app_job()
        #更新数据库
        if obj.sqlno or obj.pckno:
            message += obj.build_db_job() 
        print(message)

        # 基线邮件主题
        mailtheme = obj.app.project.name + '-' + obj.app.env.name + '-' + \
            obj.created.strftime("%Y%m%d") + '-' + str(obj.id)
        #收件人       
        recipients = []
        users = obj.app.project.users
        for user in users:
            if user.is_active:
                recipients.append(user.email)
        #附件
        log_dir = os.path.join(str(obj.app.project.target_dir),
                'LOG' + '_' + str(obj.id))
        attachments = fnmatch_file.find_specific_files(
            log_dir, '*log')
        #发送邮件
        send_email(recipients, mailtheme,
               'mail/version/baseline.html', attachments, baseline=obj
                )

        result = schema.dump(obj).data
        result.update({'detail':message})
        if result['data'].get('links', {}).get('self'):
            final_result = (result, 201, {'Location': result['data']['links']['self']})
        else:
            final_result = (result, 201)

        result = self.after_post(final_result)
        
        return result

        
    # def after_create_object(self, obj, data, view_kwargs):
    #     """Make work after create object"""
    #     message = ''
    #     #更新应用程序
    #     if obj.versionno:
    #         message += obj.build_app_job()
    #     #更新数据库
    #     if obj.sqlno or obj.pckno:
    #         message += obj.build_db_job() 
    #     print(message)

    #     # 基线邮件主题
    #     mailtheme = obj.app.project.name + '-' + obj.app.env.name + '-' + \
    #         obj.created.strftime("%Y%m%d") + '-' + str(obj.id)
    #     #收件人       
    #     recipients = []
    #     users = obj.app.project.users
    #     for user in users:
    #         if user.is_active:
    #             recipients.append(user.email)
    #     #附件
    #     log_dir = os.path.join(str(obj.app.project.target_dir),
    #             'LOG' + '_' + str(obj.id))
    #     attachments = fnmatch_file.find_specific_files(
    #         log_dir, '*log')
    #     #发送邮件
    #     send_email(recipients, mailtheme,
    #            'mail/version/baseline.html', attachments, baseline=obj
    #             )
    
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

    def after_update_object(self, obj, data, view_kwargs):
        """Make work after update object""" 
        message = ''
        #更新应用程序
        if obj.versionno:
            message += obj.build_app_job()
        #更新数据库
        if obj.sqlno or obj.pckno:
            message += obj.build_db_job() 
        print(message)

        # 基线邮件主题
        mailtheme = obj.app.project.name + '-' + obj.app.env.name + '-' + \
            obj.created.strftime("%Y%m%d") + '-' + str(obj.id)
        #收件人       
        recipients = []
        users = obj.app.project.users
        for user in users:
            if user.is_active:
                recipients.append(user.email)
        #附件
        log_dir = os.path.join(str(obj.app.project.target_dir),
                'LOG' + '_' + str(obj.id))
        attachments = fnmatch_file.find_specific_files(
            log_dir, '*log')
        #发送邮件
        send_email(recipients, mailtheme,
               'mail/version/baseline.html', attachments, baseline=obj
                )
    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline,
                  'methods': {'after_update_object': after_update_object}
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