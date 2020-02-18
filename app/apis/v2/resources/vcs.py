import os

from flask import request, g
from flask_rest_jsonapi import (Api, ResourceDetail, ResourceList,
                                ResourceRelationship)


from app import db, flask_app
from app.apis.v2 import api
from app.models.version import Baseline, Blstatus, Package

from app.apis.v2.schemas.vcs import  BaselineSchema, BlstatusSchema, PackageSchema
from app.apis.v2.auth import auth_required
from app.utils import execute_cmd, fnmatch_file, switch_char
from app.localemail import send_email

# Create resource managers
class BaselineList(ResourceList):
    decorators = auth_required,
    
    def before_post(self, args, kwargs, data=None):
        """Hook to make custom work before post method"""
        print('before_post before data:'+ str(data))
        data['developer_id'] = g.current_user.id
        data['updateno'] = 1
        data['status_id'] =5
        print('before_post aftrt data:'+ str(data))

    def after_create_object(self, obj, data, view_kwargs):
        """Make work after create object"""
        print('after create object')
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
                  'methods': {'after_create_object': after_create_object}}

class BaselineDetail(ResourceDetail):

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