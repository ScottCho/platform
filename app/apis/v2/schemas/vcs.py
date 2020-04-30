# -*- coding: utf-8 -*-

from marshmallow_jsonapi.flask import Relationship, Schema
from marshmallow_jsonapi import fields


# Create logical data abstraction
class BaselineSchema(Schema):
    class Meta:
        type_ = 'baseline'
        self_view = 'baseline_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'baseline_list'

    id = fields.Integer(dump_only=True)
    content = fields.Str()
    sqlno = fields.Str(allow_none=True)
    pckno = fields.Str(allow_none=True)
    rollbackno = fields.Str(allow_none=True)
    created = fields.Str()
    updateno = fields.Str()
    mantisno = fields.Str(allow_none=True)
    jenkins_last_build = fields.Boolean(allow_none=True)
    jenkins_build_number = fields.Integer(allow_none=True)
    versionno = fields.Str(allow_none=True)
    mark = fields.Str(allow_none=True)
    app_id = fields.Integer()
    package_id = fields.Integer(allow_none=True)
    developer_id = fields.Integer()
    status_id = fields.Integer()
    status_name = fields.Function(lambda obj: "{}".format(obj.status.name))
    package_name = fields.Function(lambda obj: "{}".format(obj.package.name))
    app_name = fields.Function(lambda obj: "{}".format(obj.app.name))
    developer_username = fields.Function(
        lambda obj: "{}".format(obj.developer.username))
    project_name = fields.Function(
        lambda obj: "{}".format(obj.app.project.name))
    project_id = fields.Function(lambda obj: "{}".format(obj.app.project.id))
    issue_category_id = fields.Integer(allow_none=True)
    issue_category_name = fields.Function(
        lambda obj: "{}".format(obj.issue_category.name))
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
                          related_view='status_detail',
                          related_view_kwargs={'id': '<status_id>'},
                          schema='StatusSchema',
                          type_='status')
    package = Relationship(self_view='baseline_package',
                           self_view_kwargs={'id': '<id>'},
                           related_view='package_detail',
                           related_view_kwargs={'id': '<package_id>'},
                           schema='PackageSchema',
                           type_='package')

    issue_bugs = Relationship(self_view='baseline_bugs',
                              self_view_kwargs={'id': '<id>'},
                              related_view='issue_bug_list',
                              related_view_kwargs={'id': '<id>'},
                              many=True,
                              schema='IssueBugSchema',
                              type_='issue_bug')

    issue_tasks = Relationship(self_view='baseline_tasks',
                               self_view_kwargs={'id': '<id>'},
                               related_view='issue_task_list',
                               related_view_kwargs={'id': '<id>'},
                               many=True,
                               schema='IssueTaskSchema',
                               type_='issue_task')

    issue_requirements = Relationship(self_view='baseline_requirements',
                                      self_view_kwargs={'id': '<id>'},
                                      related_view='issue_requirement_list',
                                      related_view_kwargs={'id': '<id>'},
                                      many=True,
                                      schema='IssueRequirementSchema',
                                      type_='issue_requirement')

    issue_category = Relationship(
        self_view='baseline_issue_category',
        self_view_kwargs={'id': '<id>'},
        related_view='issue_category_detail',
        related_view_kwargs={'id': '<issue_category_id>'},
        schema='IssueCategorySchema',
        type_='issue_category')


class PackageSchema(Schema):
    class Meta:
        type_ = 'package'
        self_view = 'package_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'package_list'

    id = fields.Integer(dump_only=True)
    name = fields.Str()
    features = fields.Str(allow_none=True)
    rlsdate = fields.Str()
    blineno = fields.Str()
    merge_blineno = fields.Str()
    remark = fields.Str(allow_none=True)
    project_id = fields.Integer()
    env_id = fields.Integer()
    package_count = fields.Str()
    project_name = fields.Function(lambda obj: "{}".format(obj.project.name))
    env_name = fields.Function(lambda obj: "{}".format(obj.env.name))
    status_id = fields.Integer()
    status_name = fields.Function(lambda obj: "{}".format(obj.status.name))
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
    baselines = Relationship(self_view='package_baselines',
                             self_view_kwargs={'id': '<id>'},
                             related_view='baseline_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='BaselineSchema',
                             type_='baseline')