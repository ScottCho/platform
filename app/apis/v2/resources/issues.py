# -*- coding: utf-8 -*-

import csv
import os

from flask import g, jsonify, request
from flask.views import MethodView
from flask_rest_jsonapi import ResourceList, ResourceRelationship

from app import db, redis_cli
from app.apis.v2 import api, api_v2
from app.apis.v2.auth import auth_required
from app.apis.v2.errors import api_abort
from app.apis.v2.schemas.issues import (IssueBugSchema, IssueCategorySchema,
                                        IssueModuleSchema, IssuePrioritySchema,
                                        IssueReproducibilitySchema,
                                        IssueRequirementSchema,
                                        IssueSeveritySchema, IssueSourceSchema,
                                        IssueTaskSchema)
from app.models.auth import User
from app.models.baseconfig import Status
from app.models.issues import (IssueBug, IssueCategory, IssueModule,
                               IssuePriority, IssueReproducibility,
                               IssueRequirement, IssueSeverity, IssueSource,
                               IssueTask)
from app import flask_app
from . import BaseResourceDetail
from werkzeug.utils import secure_filename


# Create resource managers
# 问题来源
class IssueSourceList(ResourceList):

    decorators = (auth_required, )
    schema = IssueSourceSchema
    data_layer = {'session': db.session, 'model': IssueSource}


class IssueSourceDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssueSourceSchema
    data_layer = {'session': db.session, 'model': IssueSource}


class IssueSourceRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssueSourceSchema
    data_layer = {'session': db.session, 'model': IssueSource}


# 问题模块
class IssueModuleList(ResourceList):

    decorators = (auth_required, )
    schema = IssueModuleSchema
    data_layer = {'session': db.session, 'model': IssueModule}


class IssueModuleDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssueModuleSchema
    data_layer = {'session': db.session, 'model': IssueModule}


class IssueModuleRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssueModuleSchema
    data_layer = {'session': db.session, 'model': IssueModule}


# 问题再现性
class IssueReproducibilityList(ResourceList):

    decorators = (auth_required, )
    schema = IssueReproducibilitySchema
    data_layer = {'session': db.session, 'model': IssueReproducibility}


class IssueReproducibilityDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssueReproducibilitySchema
    data_layer = {'session': db.session, 'model': IssueReproducibility}


class IssueReproducibilityRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssueReproducibilitySchema
    data_layer = {'session': db.session, 'model': IssueReproducibility}


# 问题严重性
class IssueSeverityList(ResourceList):

    decorators = (auth_required, )
    schema = IssueSeveritySchema
    data_layer = {'session': db.session, 'model': IssueSeverity}


class IssueSeverityDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssueSeveritySchema
    data_layer = {'session': db.session, 'model': IssueSeverity}


class IssueSeverityRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssueSeveritySchema
    data_layer = {'session': db.session, 'model': IssueSeverity}


# 问题优先级
class IssuePriorityList(ResourceList):

    decorators = (auth_required, )
    schema = IssuePrioritySchema
    data_layer = {'session': db.session, 'model': IssuePriority}


class IssuePriorityDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssuePrioritySchema
    data_layer = {'session': db.session, 'model': IssuePriority}


class IssuePriorityRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssuePrioritySchema
    data_layer = {'session': db.session, 'model': IssuePriority}


# 问题类别
class IssueCategoryList(ResourceList):

    decorators = (auth_required, )
    schema = IssueCategorySchema
    data_layer = {'session': db.session, 'model': IssueCategory}


class IssueCategoryDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssueCategorySchema
    data_layer = {'session': db.session, 'model': IssueCategory}


class IssueCategoryRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssueCategorySchema
    data_layer = {'session': db.session, 'model': IssueCategory}


# 需求
class IssueRequirementList(ResourceList):

    decorators = (auth_required, )

     # 返回当前用户登录的项目相关结果
    def query(self, view_kwargs):
        current_project_id = g.current_project.id if g.current_project else None
        query_ = self.session.query(IssueRequirement).filter_by(
                project_id=current_project_id).order_by(IssueRequirement.id.desc())
        return query_

    def after_post(self, result):
        """提交后，将动态提交到redis中"""
        redis_cli.lpush(
            'frog_list',
            g.current_user.username + '发布' + g.current_project.name + '需求')
        return result

    schema = IssueRequirementSchema
    data_layer = {
        'session': db.session,
        'model': IssueRequirement,
        'methods': {
            'query': query
        }
    }


class IssueRequirementDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssueRequirementSchema
    data_layer = {'session': db.session, 'model': IssueRequirement}


class IssueRequirementRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssueRequirementSchema
    data_layer = {'session': db.session, 'model': IssueRequirement}


# 任务
class IssueTaskList(ResourceList):

    decorators = (auth_required, )

    # 返回当前用户登录的项目相关结果
    def query(self, view_kwargs):
        current_project_id = g.current_project.id if g.current_project else None
        query_ = self.session.query(IssueTask).filter_by(
                project_id=current_project_id).order_by(IssueTask.id.desc())
        return query_

    def after_post(self, result):
        """提交后，将动态提交到redis中"""
        redis_cli.lpush(
            'frog_list',
            g.current_user.username + '发布' + g.current_project.name + '任务')
        return result

    schema = IssueTaskSchema
    data_layer = {
        'session': db.session,
        'model': IssueTask,
        'methods': {
            'query': query
        }
    }


class IssueTaskDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssueTaskSchema
    data_layer = {'session': db.session, 'model': IssueTask}


class IssueTaskRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssueTaskSchema
    data_layer = {'session': db.session, 'model': IssueTask}


# Bug
class IssueBugList(ResourceList):

    decorators = (auth_required, )

    # 返回当前用户登录的项目相关结果
    def query(self, view_kwargs):
        current_project_id = g.current_project.id if g.current_project else None
        query_ = self.session.query(IssueBug).filter_by(
                project_id=current_project_id).order_by(IssueBug.id.desc())
        return query_

    def after_post(self, result):
        """提交后，将动态提交到redis中"""
        redis_cli.lpush(
            'frog_list',
            g.current_user.username + '发布' + g.current_project.name + '任务')
        return result

    schema = IssueBugSchema
    data_layer = {
        'session': db.session,
        'model': IssueBug,
        'methods': {
            'query': query
        }
    }


class IssueBugDetail(BaseResourceDetail):
    decorators = (auth_required, )

    schema = IssueBugSchema
    data_layer = {'session': db.session, 'model': IssueBug}


class IssueBugRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = IssueBugSchema
    data_layer = {'session': db.session, 'model': IssueBug}


class UploadIssueAPI(MethodView):
    decorators = [auth_required]

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'xls', 'csv'}
        return '.' in filename and filename.rsplit(
            '.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def post(self):
        # check if the post request has the file part
        if 'file' not in request.files:
            return api_abort(400, 'No file part')
        file = request.files['file']
        issue = request.args.get('issue')  # issue为bug requirement task
        # if user does not select file, browser also
        # submit an empty part without filename
        issue_source =''
        filename = file.filename
        if filename == '':
            return api_abort(400, 'No selected file')
        if file and self.allowed_file(filename):
            issue_source = filename.split('_')[0]
            filename = secure_filename(filename)
            file_path = os.path.join(flask_app.config['UPLOAD_FOLDER'],
                                     filename)
            file.save(file_path)
            with open(file_path, newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                if issue == 'issue_bug':
                    IssueBug.upload_issue(csv_reader)
                elif issue == 'issue_requirement':
                    IssueRequirement.upload_issue(csv_reader)
                elif issue == 'issue_task':
                    IssueTask.upload_issue(csv_reader)
            redis_cli.lpush(
                'frog_list',
                g.current_user.username + '导入了issues')
            return jsonify(data=[{'status': 200, 'detail': '导入成功'}])


# Create endpoints
# 问题来源
api.route(IssueSourceList, 'issue_source_list', '/api/issue_sources')
api.route(IssueSourceDetail, 'issue_source_detail', '/api/issue_sources/<id>')
api.route(IssueSourceRelationship, 'issue_source_requirements',
          '/api/issue_sources/<int:id>/relationships/issue_requirements')
api.route(IssueSourceRelationship, 'issue_source_bugs',
          '/api/issue_sources/<int:id>/relationships/issue_bugs')

# 问题模块
api.route(IssueModuleList, 'issue_module_list', '/api/issue_modules')
api.route(IssueModuleDetail, 'issue_module_detail', '/api/issue_module/<id>')
api.route(IssueModuleRelationship, 'issue_module_requirements',
          '/api/issue_module/<int:id>/relationships/issue_requirements')
api.route(IssueModuleRelationship, 'issue_module_bugs',
          '/api/issue_module/<int:id>/relationships/issue_bugs')

# 问题再现性
api.route(IssueReproducibilityList, 'issue_reproducibility_list',
          '/api/issue_reproducibility')
api.route(IssueReproducibilityDetail, 'issue_reproducibility_detail',
          '/api/issue_reproducibility/<id>')
api.route(IssueReproducibilityRelationship, 'issue_reproducibility_bugs',
          '/api/issue_reproducibility/<int:id>/relationships/issue_bugs')

# 问题严重性
api.route(IssueSeverityList, 'issue_severity_list', '/api/issue_severity')
api.route(IssueSeverityDetail, 'issue_severity_detail',
          '/api/issue_severity/<id>')
api.route(IssueSeverityRelationship, 'issue_severity_bugs',
          '/api/issue_severity/<int:id>/relationships/issue_bugs')

# 问题优先级
api.route(IssuePriorityList, 'issue_priority_list', '/api/issue_priority')
api.route(IssuePriorityDetail, 'issue_priority_detail',
          '/api/issue_priority/<id>')
api.route(IssuePriorityRelationship, 'issue_priority_requirements',
          '/api/issue_priority/<int:id>/relationships/issue_requirements')
api.route(IssuePriorityRelationship, 'issue_priority_bugs',
          '/api/issue_priority/<int:id>/relationships/issue_bugs')
api.route(IssuePriorityRelationship, 'issue_priority_tasks',
          '/api/issue_priority/<int:id>/relationships/issue_tasks')

# 问题类别
api.route(IssueCategoryList, 'issue_category_list', '/api/issue_categories')
api.route(IssueCategoryDetail, 'issue_category_detail',
          '/api/issue_categories/<id>')
api.route(IssueCategoryRelationship, 'issue_category_baselines',
          '/api/issue_categories/<int:id>/relationships/baselines')

# 需求
api.route(IssueRequirementList, 'issue_requirement_list',
          '/api/issue_requirements')
api.route(IssueRequirementDetail, 'issue_requirement_detail',
          '/api/issue_requirements/<id>')
api.route(IssueRequirementRelationship, 'issue_requirement_tasks',
          '/api/issue_requirements/<int:id>/relationships/issue_tasks')
api.route(IssueRequirementRelationship, 'issue_requirement_status',
          '/api/issue_requirements/<int:id>/relationships/status')
api.route(IssueRequirementRelationship, 'issue_requirement_baselines',
          '/api/issue_requirements/<int:id>/relationships/baselines')

# task
api.route(IssueTaskList, 'issue_task_list', '/api/issue_tasks')
api.route(IssueTaskDetail, 'issue_task_detail', '/api/issue_tasks/<id>')
api.route(IssueTaskRelationship, 'issue_task_status',
          '/api/issue_tasks/<int:id>/relationships/status')
api.route(IssueTaskRelationship, 'issue_task_requirement',
          '/api/issue_tasks/<int:id>/relationships/issue_requirement')
api.route(IssueTaskRelationship, 'issue_task_baselines',
          '/api/issue_tasks/<int:id>/relationships/baselines')

# bug
api.route(IssueBugList, 'issue_bug_list', '/api/issue_bugs')
api.route(IssueBugDetail, 'issue_bug_detail', '/api/issue_bugs/<id>')
api.route(IssueBugRelationship, 'issue_bug_status',
          '/api/issue_bugs/<int:id>/relationships/status')
api.route(IssueRequirementRelationship, 'issue_bug_baselines',
          '/api/issue_bugs/<int:id>/relationships/baselines')

# issue导入
api_v2.add_url_rule('/issue/upload',
                    view_func=UploadIssueAPI.as_view('issue_upload'),
                    methods=[
                        'POST',
                    ])
