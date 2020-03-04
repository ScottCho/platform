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
from app.models.service import App

from app.apis.v2.schemas.vcs import  BaselineSchema, BlstatusSchema, PackageSchema
from app.apis.v2.auth import auth_required
from app.utils import execute_cmd, fnmatch_file, switch_char
from app.localemail import send_email
from app.utils.jenkins import get_jenkins_job

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
        obj = self._data_layer.get_object({'id':result[0]['data']['id']})
        message = obj.update_baseline()
        # 发送邮件
        obj.baseline_email()
        # 更新结果返回
        result[0].update({'detail': message})
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
        obj = self._data_layer.get_object({'id':result['data']['id']})
        message = obj.update_baseline()
        # 发送邮件
        obj.baseline_email()
        # 更新结果返回
        result.update({'detail': message})
        return result

    # 改写成批量删除，kwargs={'id':'[1,2,3]'}
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if len(ids) == 1:
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
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

    #　处理更新包的默认内容
    def before_post(self, args, kwargs, data=None):
        """Hook to make custom work before post method""" 
        blineno = data['blineno']
        bdate  = data['rlsdate']
        env_id = data['env_id']
        #将基线按app分组 {<App 1>: [<Baseline 1>,  <Baseline 2>],<App 2>: [<Baseline 3>]}
        app_dict={}
        merge_list=[]
        for bid in blineno.split(','):
            baseline = Baseline.query.filter_by(id=int(bid)).first()
            app = baseline.app
            if app not in app_dict.keys():
                app_dict.update({app:[baseline]})
            else:
                app_dict[app].append(baseline)

        #将相同的app合并成一条基线
        for app_key, baseline_list in app_dict.items():
            versionnos = '' 
            sqlnos = ''
            pcknos = ''
            rollbacknos = ''
            for baseline in baseline_list:
                if baseline.sqlno:
                    sqlnos = '{},{}'.format(sqlnos,baseline.sqlno)
                if baseline.versionno:
                    versionnos = '{},{}'.format(versionnos,baseline.versionno)
                if baseline.pckno:
                    pcknos = '{},{}'.format(pcknos,baseline.pckno)
                if baseline.rollbackno:
                    rollbacknos = '{},{}'.format(rollbacknos,baseline.rollbackno)
               
            # 将多条基线合并到同一条
            subsystem_id = app_key.subsystem_id
            project_id = app_key.project_id
            merge_app = App.query.filter_by(project_id=project_id,subsystem_id=subsystem_id,env_id=env_id).first()
            merge_baseline = Baseline(
                sqlno=sqlnos.strip(','),
                versionno=versionnos.strip(','),
                pckno=pcknos.strip(','),
                rollbackno=rollbacknos.strip(','),
                created=bdate,
                app_id=merge_app.id,
                content='合并发布',
                developer_id=g.current_user.id,
                updateno=1,
                status_id=5
            )
            db.session.add(merge_baseline)    
            db.session.commit()
            merge_list.append(merge_baseline)
        merge_blineno = ','.join(str(bline.id) for bline in merge_list)
        data['merge_blineno'] = merge_blineno

    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageDetail(ResourceDetail):
    decorators = (auth_required,)

    def before_patch(self, args, kwargs, data=None):
        """Hook to make custom work before patch method"""
        env_id=data['env_id']
        rlsdate=data['rlsdate']
        project_id=data['project_id']
        merge_blineno = data['merge_blineno']
        original_merge_bline_list = merge_blineno.split(',')
        merge_list = []
        blineno = data['blineno']
        change_blineno_list = blineno.split(',')

        #删除原始的合并的基线
        for no in original_merge_bline_list:
            baseline = Baseline.query.filter_by(id=no).first()
            if baseline:
                db.session.delete(baseline)
                db.session.commit()

        #将相同的app合并成一条基线
        #{<App 1>: [<Baseline 1>,  <Baseline 2>],<App 2>: [<Baseline 3>]}
        app_dict={}
        for no in  change_blineno_list:
            baseline = Baseline.query.get_or_404(no)
            app = baseline.app
            if app not in app_dict.keys():
                app_dict.update({app:[baseline]})
            else:
                app_dict[app].append(baseline)
        for app_key in app_dict.keys():
            versionnos = '' 
            sqlnos = ''
            pcknos = ''
            rollbacknos = ''
            baseline_list = app_dict[app_key]
            for baseline in baseline_list:
                bsqlno = baseline.sqlno
                bversionno = baseline.versionno
                bpckno = baseline.pckno
                brollbackno = baseline.rollbackno
                # 拼接基线
                if bsqlno:
                    sqlnos = (str(bsqlno) + ',' + sqlnos).strip(',')
                if bversionno:
                    versionnos = (str(bversionno) + ',' + versionnos).strip(',')
                if bpckno:
                    pcknos = (str(bpckno) + ',' + pcknos).strip(',')
                if brollbackno:
                    rollbacknos = (str(brollbackno) + ',' + rollbacknos).strip(',')

            # 将多条基线合并到同一条
            subsystem_id = app_key.subsystem_id
            merge_app = App.query.filter_by(project_id=project_id,env_id=env_id,subsystem_id=subsystem_id).first()
            merge_baseline = Baseline(sqlno=sqlnos,
                                  versionno=versionnos,
                                  pckno=pcknos,
                                  rollbackno=rollbacknos,
                                  created=rlsdate,
                                  app_id=merge_app.id,
                                  content='合并发布',
                                  developer_id=g.current_user.id,
                                  updateno=1,
                                  status_id=17
                                  )
            db.session.add(merge_baseline)    
            db.session.commit()
            merge_list.append(merge_baseline)

        #  设置package中的merge_blineno的值
        merge_blineno = ','.join(str(bline.id) for bline in merge_list)
        data['merge_blineno'] = merge_blineno


    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}   

class PackageMerge(ResourceDetail):
    decorators = (auth_required,)

    def after_get(self, result):
        package = self._data_layer.get_object({'id':result['data']['id']})
        detail = package.package_merge()
        result.update({'detail': detail})
        return result

    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageDeploy(ResourceDetail):
    decorators = (auth_required,)

    def after_get(self, result):
        package = self._data_layer.get_object({'id':result['data']['id']})
        detail = package.package_deploy()
        result.update({'detail': detail})
        return result

    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageRelease(ResourceDetail):
    decorators = (auth_required,)

    def after_get(self, result):
        package = self._data_layer.get_object({'id':result['data']['id']})
        detail = package.package_release()
        result.update({'detail': detail})
        return result

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
# 合并基线
api.route(PackageMerge, 'package_merge', '/api/packages/merge/<int:id>')
# 部署更新包
api.route(PackageDeploy, 'package_deploy', '/api/packages/deploy/<int:id>')
# 发布更新包
api.route(PackageRelease, 'package_release', '/api/packages/release/<int:id>')