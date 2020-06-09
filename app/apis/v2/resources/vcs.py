import os
from datetime import datetime

from flask import g, current_app
from flask.views import MethodView
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)

from app import db, redis_cli
from app.apis.v2 import api, api_v2
from app.apis.v2.auth import auth_required
from app.apis.v2.errors import api_abort
from app.apis.v2.schemas.vcs import BaselineSchema, PackageSchema
from app.models.auth import Project
from app.models.version import Baseline, Package

from app.utils.mypath import dir_remake
from . import BaseResourceDetail


# Create resource managers
class BaselineList(ResourceList):
    decorators = (auth_required, )

    # 返回当前用户登录的项目相关基线结果
    def query(self, view_kwargs):
        app_ids = []
        if g.current_project:
            current_project = g.current_project
            apps = current_project.apps
            app_ids = [app.id for app in apps]
        else:
            app_ids = []
        query_ = self.session.query(Baseline).filter(
            Baseline.app_id.in_(app_ids)).order_by(Baseline.id.desc())
        return query_

    # 处理基线的默认内容,开发者为当前登录用户
    def before_post(self, args, kwargs, data=None):
        """Hook to make custom work before post method"""
        data['developer_id'] = g.current_user.id

    def after_post(self, result):
        """提交后，将动态提交到redis中"""
        redis_cli.lpush(
            'frog_list',
            g.current_user.username + '发布' + g.current_project.name + '基线')
        return result

    schema = BaselineSchema
    data_layer = {
        'session': db.session,
        'model': Baseline,
        'methods': {
            'query': query
        }
    }


class BaselineDetail(BaseResourceDetail):
    decorators = (auth_required, )

    def after_patch(self, result):
        """Hook to make custom work after patch method"""
        redis_cli.lpush(
            'frog_list',
            g.current_user.username + '重新发布' + g.current_project.name + '基线')
        return result

    schema = BaselineSchema
    data_layer = {'session': db.session, 'model': Baseline}


class BaselineRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = BaselineSchema
    data_layer = {'session': db.session, 'model': Baseline}


# 更新包
class PackageList(ResourceList):
    decorators = (auth_required, )

    # 返回当前用户登录的项目相关结果
    def query(self, view_kwargs):
        current_project_id = g.current_project.id if g.current_project else None
        query_ = self.session.query(Package).filter_by(
            project_id=current_project_id).order_by(Package.id.desc())
        return query_

    def before_post(self, args, kwargs, data=None):
        """Hook to make custom work before post method
            根据提供的项目、日期、和次数生成更新包的名字  WellLink_20200423_01
        """
        bdate = data['rlsdate']
        package_count = data.get('package_count', '01')
        project_id = data.get('project_id')
        project_name = Project.query.get(project_id).name
        bdate = data.get('rlsdate',
                         datetime.now().strftime("%Y%m%d")).replace(
                             '-', '')
        name = "{}_{}_{}".format(project_name, bdate, package_count)
        data['name'] = name  # 更新包名字

    def after_post(self, result):
        """Hook to make custom work after post method
        根据更新包中的合并基线，将其按照app分组合并
        并添加合并基线
        """
        obj = self._data_layer.get_object({'id': result[0]['data']['id']})
        # 重建更新包
        obj.create_package_dir()
        # 提交更新包后的处理
        merge_blineno = obj.package_after_post()
        obj.merge_blineno = merge_blineno
        db.session.add(obj)
        db.session.commit()
        redis_cli.lpush(
            'frog_list',
            g.current_user.username + '发布' + g.current_project.name + '更新包')
        return result
        return result

    schema = PackageSchema
    data_layer = {
        'session': db.session,
        'model': Package,
        'methods': {
            'query': query
        }
    }


class PackageDetail(BaseResourceDetail):
    decorators = (auth_required, )

    def before_patch(self, args, kwargs, data=None):
        """Hook to make custom work before patch method
           将更新包的状态改为重新录入，并且重建目录
        """
        try:
            obj = self._data_layer.get_object({'id': kwargs['id']})
            # 重建更新包
            obj.create_package_dir()
            merge_blineno = obj.package_after_post()
            data['merge_blineno'] = merge_blineno
            data['status_id'] = 216
            rlsdate = data['rlsdate'].split()[0].replace('-','')
            package_count = data['package_count']
            name = f'{g.current_project.name}_{rlsdate}_{package_count}'
            data['name'] = name
        except Exception as e:
            current_app.logger.error('更新包编辑失败：\n'+str(e))
            return api_abort(400, detail='更新包编辑失败：\n'+str(e))


    def after_patch(self, result):
        """Hook to make custom work after patch method"""
        redis_cli.lpush(
            'frog_list',
            g.current_user.username + '重新发布' + g.current_project.name + '更新包')
        return result

    schema = PackageSchema
    data_layer = {'session': db.session, 'model': Package}


class PackageRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = PackageSchema
    data_layer = {'session': db.session, 'model': Package}


class PackageMerge(ResourceDetail):
    decorators = (auth_required, )

    def after_get(self, result):
        package = self._data_layer.get_object({'id': result['data']['id']})
        try:
            detail = package.package_merge()
            result.update({'detail': detail})
        except Exception as e:
            detail = '更新包合并失败: '+str(e)
            current_app.logger.error(str(e))
            return api_abort(400, detail=str(e))
        return result

    schema = PackageSchema
    data_layer = {'session': db.session, 'model': Package}


class PackageDeploy(ResourceDetail):
    '''
    更新包部署
    '''
    decorators = (auth_required, )

    def after_get(self, result):
        package = self._data_layer.get_object({'id': result['data']['id']})
        try:
            detail = package.package_deploy()
            result.update({'detail': detail})
        except Exception as e:
            return api_abort(400, detail='部署失败: '+str(e))
        return result

    schema = PackageSchema
    data_layer = {'session': db.session, 'model': Package}


class PackageRelease(ResourceDetail):
    '''
    更新包发布
    '''
    decorators = (auth_required, )

    def after_get(self, result):
        package = self._data_layer.get_object({'id': result['data']['id']})
        detail = ''
        try:
            if package.status_id == 211:
                detail = '更新包状态为已交付，请重新编辑后再发布'
            else:
                detail = package.package_release()
        except Exception as e:
            detail = '更新包发布失败: '+str(e)
            current_app.logger.error(str(e))
        result.update({'detail': detail})
        return result

    schema = PackageSchema
    data_layer = {'session': db.session, 'model': Package}


class PackageDownloadAPI(MethodView):
    '''
    更新包下载
    '''
    def get(self, package_id):
        package = Package.query.get(package_id)
        return package.package_download()


class BaselineUpdate(ResourceDetail):
    '''
    基线更新
    '''
    decorators = (auth_required, )

    def after_get(self, result):
        obj = self._data_layer.get_object({'id': result['data']['id']})
        obj.updateno += 1
        obj.status_id = 203
        db.session.add(obj)
        db.session.commit()
        try:
            update_dir = os.path.join(obj.app.project.target_dir, str(obj.id))
            dir_remake(update_dir)
            if obj.sqlno or obj.pckno:
                obj.update_db()
            if obj.versionno:
                obj.update_app()
        except Exception as e:
            return api_abort(400, detail=str(e))
        else:
            # 发送邮件
            if not current_app.debug:
                obj.send_baseline_email()
        return result

    schema = BaselineSchema
    data_layer = {'session': db.session, 'model': Baseline}


class PackageDownloadAPI(MethodView):
    '''
    更新包下载
    '''
    def get(self, package_id):
        package = Package.query.get(package_id)
        return package.package_download()


class BaselineLogView(ResourceDetail):
    '''
    基线日志查看
    '''
    decorators = (auth_required, )

    def after_get(self, result):
        try:
            obj = self._data_layer.get_object({'id': result['data']['id']})
            log = obj.log_view()
        except Exception as e:
            print(e)
            return api_abort(400, detail=f'获取不到基线{str(obj.id)}的日志,{str(e)}')
        else:
            result.update({'detail': log})
        return result

    schema = BaselineSchema
    data_layer = {'session': db.session, 'model': Baseline}


class PackageLogView(ResourceDetail):
    '''
    更新包日志查看
    '''
    decorators = (auth_required, )

    def after_get(self, result):
        try:
            obj = self._data_layer.get_object({'id': result['data']['id']})
            log = obj.log_view()
        except Exception as e:
            print(e)
            return api_abort(400, detail=f'获取不到更新包{str(obj.id)}的日志,{str(e)}')
        else:
            result.update({'detail': log})
        return result

    schema = PackageSchema
    data_layer = {'session': db.session, 'model': Package}


# Create endpoints
# 基线
api.route(BaselineList, 'baseline_list', '/api/baselines')
api.route(BaselineDetail, 'baseline_detail', '/api/baselines/<id>')
api.route(BaselineRelationship, 'baseline_developer',
          '/api/baselines/<int:id>/relationships/developer')
api.route(BaselineRelationship, 'baseline_app',
          '/api/baselines/<int:id>/relationships/app')
api.route(BaselineRelationship, 'baseline_status',
          '/api/baselines/<int:id>/relationships/status')
api.route(BaselineRelationship, 'baseline_package',
          '/api/baselines/<int:id>/relationships/package')
api.route(BaselineRelationship, 'baseline_bugs',
          '/api/baselines/<int:id>/relationships/bug')
api.route(BaselineRelationship, 'baseline_tasks',
          '/api/baselines/<int:id>/relationships/task')
api.route(BaselineRelationship, 'baseline_requirements',
          '/api/baselines/<int:id>/relationships/requirement')
api.route(BaselineRelationship, 'baseline_issue_category',
          '/api/baselines/<int:id>/relationships/isssue_category')

# 更新包
api.route(PackageList, 'package_list', '/api/packages')
api.route(PackageDetail, 'package_detail', '/api/packages/<id>')
api.route(PackageRelationship, 'package_project',
          '/api/packages/<int:id>/relationships/project')
api.route(PackageRelationship, 'package_env',
          '/api/packages/<int:id>/relationships/env')
api.route(PackageRelationship, 'package_baselines',
          '/api/packages/<int:id>/relationships/baselines')
# 合并基线
api.route(PackageMerge,
          'package_merge',
          '/api/packages/merge/<int:id>',
          url_rule_options={'methods': [
              'GET',
          ]})
# 部署更新包
api.route(PackageDeploy,
          'package_deploy',
          '/api/packages/deploy/<int:id>',
          url_rule_options={'methods': [
              'GET',
          ]})
# 发布更新包
api.route(PackageRelease, 'package_release', '/api/packages/release/<int:id>')

# 更新基线,只提供GET方法
api.route(BaselineUpdate,
          'baseline_update',
          '/api/baseline/update/<id>',
          url_rule_options={'methods': [
              'GET',
          ]})

# 查看基线日志
api.route(BaselineLogView,
          'baseline_log_view',
          '/api/baselines/logview/<id>',
          url_rule_options={'methods': [
              'GET',
          ]})

# 查看更新包日志
api.route(PackageLogView,
          'package_log_view',
          '/api/packages/logview/<id>',
          url_rule_options={'methods': [
              'GET',
          ]})

# 更新包下载
api_v2.add_url_rule('/packages/download/<package_id>',
                    view_func=PackageDownloadAPI.as_view('package_download'),
                    methods=[
                        'GET',
                    ])
