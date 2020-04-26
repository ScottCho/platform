import os
from datetime import datetime

from flask import g, make_response, request, url_for
from flask.views import MethodView, MethodViewType
from flask.wrappers import Response as FlaskResponse
from flask_rest_jsonapi import (Api, ResourceDetail, ResourceList,
                                ResourceRelationship)
from flask_rest_jsonapi.data_layers.alchemy import SqlalchemyDataLayer
from flask_rest_jsonapi.data_layers.base import BaseDataLayer
from flask_rest_jsonapi.decorators import (check_headers,
                                           check_method_requirements,
                                           jsonapi_exception_formatter)
from flask_rest_jsonapi.exceptions import (BadRequest, InvalidType,
                                           RelationNotFound)
from flask_rest_jsonapi.pagination import add_pagination_links
from flask_rest_jsonapi.querystring import QueryStringManager as QSManager
from flask_rest_jsonapi.schema import (compute_schema, get_model_field,
                                       get_relationships)
from flask_rest_jsonapi.utils import JSONEncoder
from marshmallow import ValidationError
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from werkzeug.wrappers import Response

from app import db, flask_app
from app.apis.v2 import api, api_v2
from app.apis.v2.auth import auth_required
from app.apis.v2.errors import api_abort
from app.apis.v2.resources.baseconfig import StatusDetail
from app.apis.v2.schemas.baseconfig import StatusSchema
from app.apis.v2.schemas.vcs import BaselineSchema, PackageSchema
from app.localemail import send_email
from app.models.baseconfig import Status
from app.models.service import App
from app.models.version import Baseline, Package
from app.utils import execute_cmd, fnmatch_file, switch_char
from app.utils.jenkins import get_jenkins_job
from app.models.auth import Project

# Create resource managers
class BaselineList(ResourceList):
    decorators = (auth_required,)

    # 如果登录用户为管理员则显示所有结果，否则只显示参与的项目的基线
    def query(self, view_kwargs):
        if g.current_user.role_id == 1:
            query_ = self.session.query(Baseline)
        else:
            projects = g.current_user.projects
            apps = []
            for project in projects:
                apps += project.apps
            app_ids = [app.id for app in apps]
            query_ = self.session.query(Baseline).filter(Baseline.app_id.in_(app_ids))
        return query_
    
    #　处理基线的默认内容,基线的默认状态为 “SIT提测”
    #  更新次数为1
    def before_post(self, args, kwargs, data=None):
        """Hook to make custom work before post method"""
        data['developer_id'] = g.current_user.id
        data['updateno'] = 1
        data['status_id'] =203
        

    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline,
                  'methods': {'query': query}
                }

class BaselineDetail(ResourceDetail):
    decorators = (auth_required,)
  
    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
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



#更新包
class PackageList(ResourceList):
    decorators = (auth_required,)

    
    def before_post(self, args, kwargs, data=None):

        """Hook to make custom work before post method
            根据提供的项目、日期、和次数生成更新包的名字  WellLink_20200423_01
        """ 
        bdate  = data['rlsdate']
        package_count = data.get('package_count'.zfill(2),'01')
        project_id = data.get('project_id')
        project_name = Project.query.get(project_id).name
        bdate = data.get('rlsdate',datetime.now().strftime("%Y%m%d")).replace('-','')    # 2020-03-31
        name = "{}_{}_{}".format(project_name, bdate, package_count)
        data['name'] = name      # 更新包名字
        

    def after_post(self, result):
        """Hook to make custom work after post method
        根据更新包中的合并基线，将其按照app分组合并
        并添加合并基线
        """
      
        obj = self._data_layer.get_object({'id':result[0]['data']['id']})
        merge_blineno = obj.baseline_group_merge()
        obj.merge_blineno = merge_blineno
        db.session.add(obj)
        db.session.commit()
        return result

    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageDetail(ResourceDetail):
    decorators = (auth_required,)

    def before_patch(self, args, kwargs, data=None):
        """Hook to make custom work before patch method"""
        obj = self._data_layer.get_object({'id':kwargs['id']})
        merge_blineno = obj.baseline_group_merge()
        data['merge_blineno'] = merge_blineno

    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id':id})
                self._data_layer.delete_object(obj, {'id':id})

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
        print(detail)
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
        print('detail:' + detail)
        result.update({'detail': detail})
        return result

    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageRelease(ResourceDetail):
    '''
    基线打包
    '''
    decorators = (auth_required,)

    def after_get(self, result):
        package = self._data_layer.get_object({'id':result['data']['id']})
        detail = package.package_release()
        result.update({'detail': detail})
        return result

    schema = PackageSchema
    data_layer = {'session': db.session,
                  'model': Package}

class PackageDownloadAPI(MethodView):
    '''
    更新包下载
    '''
    def get(self,package_id):
        package = Package.query.get(package_id)
        return package.package_download()
       

class BaselineUpdate(ResourceDetail):
    '''
    基线更新
    '''
    decorators = (auth_required,)

    def after_get(self, result):
        obj = self._data_layer.get_object({'id':result['data']['id']})
        obj.updateno += 1
        db.session.add(obj)
        db.session.commit()
        message = '*****开始更新基线*****\n'
        try:
            if obj.sqlno or obj.pckno:
                message += obj.update_db()
            if obj.versionno:
                message += obj.update_app()
        except Exception as e:
            return api_abort(400,detail=str(e))
        else:
            # 发送邮件
            obj.send_baseline_email()
            # 更新结果返回
            result.update({'detail': message})
        return result
    schema = BaselineSchema
    data_layer = {'session': db.session,
                  'model': Baseline  
                }

# Create endpoints
#基线
api.route(BaselineList, 'baseline_list', '/api/baselines')
api.route(BaselineDetail, 'baseline_detail', '/api/baselines/<id>')
api.route(BaselineRelationship, 'baseline_developer', '/api/baselines/<int:id>/relationships/developer')
api.route(BaselineRelationship, 'baseline_app', '/api/baselines/<int:id>/relationships/app')
api.route(BaselineRelationship, 'baseline_status', '/api/baselines/<int:id>/relationships/status')
api.route(BaselineRelationship, 'baseline_package', '/api/baselines/<int:id>/relationships/package')
api.route(BaselineRelationship, 'baseline_bugs', '/api/baselines/<int:id>/relationships/bug')
api.route(BaselineRelationship, 'baseline_tasks', '/api/baselines/<int:id>/relationships/task')
api.route(BaselineRelationship, 'baseline_requirements', '/api/baselines/<int:id>/relationships/requirement')
api.route(BaselineRelationship, 'baseline_issue_category', '/api/baselines/<int:id>/relationships/isssue_category')

#更新包
api.route(PackageList, 'package_list', '/api/packages')
api.route(PackageDetail, 'package_detail', '/api/packages/<id>')
api.route(PackageRelationship, 'package_project', '/api/packages/<int:id>/relationships/project')
api.route(PackageRelationship, 'package_env', '/api/packages/<int:id>/relationships/env')
api.route(PackageRelationship, 'package_baselines', '/api/packages/<int:id>/relationships/baselines')
# 合并基线
api.route(PackageMerge, 'package_merge', '/api/packages/merge/<int:id>',url_rule_options={'methods':['GET',]})
# 部署更新包
api.route(PackageDeploy, 'package_deploy', '/api/packages/deploy/<int:id>',url_rule_options={'methods':['GET',]})
# 发布更新包
api.route(PackageRelease, 'package_release', '/api/packages/release/<int:id>')
# 更新基线,只提供GET方法
api.route(BaselineUpdate, 'baseline_update', '/api/baseline/update/<id>',url_rule_options={'methods':['GET',]})


# 更新包下载
api_v2.add_url_rule('/packages/download/<package_id>', view_func=PackageDownloadAPI.as_view('package_download'), methods=['GET',])
