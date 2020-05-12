# -*- coding: utf-8 -*-

import csv
import os

from flask import g, jsonify, request
from flask.views import MethodView
from flask_rest_jsonapi import ResourceList, ResourceRelationship

from app import db
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
        if file.filename == '':
            return api_abort(400, 'No selected file')
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(flask_app.config['UPLOAD_FOLDER'],
                                     filename)
            file.save(file_path)
            with open(file_path, newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for row in csv_reader:
                    print(row)
                    if issue == 'issue_task':
                        number = row['编号']
                        summary = row['任务名称']
                        description = row['任务描述']
                        startdate = row[
                            '实际开始'] if row['实际开始'] != '0000-00-00' else None
                        enddate = row[
                            '完成时间'] if row['完成时间'] != '0000-00-00' else None
                        deadline = row[
                            '截止日期'] if row['截止日期'] != '0000-00-00' else None
                        manhour = row['最初预计']
                        status_name = row['任务状态']
                        status_id = Status.query.filter_by(
                            name=status_name).one().id
                        requirement_summary = row['相关需求']
                        requirement_id = None
                        if requirement_summary:
                            org_requirement_id = requirement_summary.split(
                                '#')[-1].strip(')')
                            requirement_id = IssueRequirement.query.filter_by(
                                number=org_requirement_id).one().id
                        assignee_name = row['指派给']
                        assignee_id = None
                        if assignee_name:
                            assignee_id = User.query.filter_by(
                                username=assignee_name).one().id
                        priority_id = row['优先级'] if row['优先级'] != '' else None
                        itask = IssueTask(number=number,
                                          summary=summary,
                                          description=description,
                                          startdate=startdate,
                                          enddate=enddate,
                                          deadline=deadline,
                                          manhour=manhour,
                                          status_id=status_id,
                                          requirement_id=requirement_id,
                                          assignee_id=assignee_id,
                                          priority_id=priority_id,
                                          project_id=g.current_project.id)
                        db.session.add(itask)
                    elif issue == 'issue_requirement':
                        number = row['编号']
                        summary = row['需求名称']
                        description = row['需求描述']
                        manhour = row['预计工时']
                        status_name = row['当前状态']
                        status_id = Status.query.filter_by(
                            name=status_name).one().id
                        requirement_summary = row['相关需求']
                        if requirement_summary:
                            requirement_id = requirement_summary.split(
                                '#')[-1].strip(')')
                        else:
                            requirement_id = None
                        assignee_name = row['指派给']
                        assignee_id = None
                        if assignee_name:
                            assignee_id = User.query.filter_by(
                                username=assignee_name).first().id
                        priority_id = row['优先级'] if row['优先级'] != '' else None
                        requirement = IssueRequirement(number=number,
                                                       summary=summary,
                                                       description=description,
                                                       manhour=manhour,
                                                       status_id=status_id,
                                                       assignee_id=assignee_id,
                                                       project_id=g.current_project.id,
                                                       priority_id=priority_id)
                        db.session.add(requirement)
                    elif issue == 'issue_bug':
                        number = row['Bug编号']
                        summary = row['Bug标题']
                        description = row['重现步骤']
                        startdate = row[
                            '指派日期'] if row['指派日期'] != '0000-00-00' else None
                        enddate = row[
                            '解决日期'] if row['解决日期'] != '0000-00-00' else None
                        status_name = row['Bug状态']
                        status_id = Status.query.filter_by(
                            name=status_name, attribute='issue').one().id
                        requirement_id = None
                        requirement_summary = row['相关需求']
                        if requirement_summary != '0':
                            org_requirement_id = requirement_summary.split(
                                '#')[-1].strip(')')
                            requirement_id = IssueRequirement.query.filter_by(
                                number=org_requirement_id).one().id
                        assignee_name = row['指派给']
                        assignee_id = None
                        if assignee_name and assignee_name != 'Closed':
                            print('指派给'*5+assignee_name)
                            assignee_id = User.query.filter_by(
                                username=assignee_name).one().id
                        priority_id = row['优先级'] if row['优先级'] != '' else None
                        bug = IssueBug(number=number,
                                       summary=summary,
                                       description=description,
                                       startdate=startdate,
                                       enddate=enddate,
                                       status_id=status_id,
                                       assignee_id=assignee_id,
                                       project_id=g.current_project.id,
                                       priority_id=priority_id)
                        db.session.add(bug)
            db.session.commit()
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
