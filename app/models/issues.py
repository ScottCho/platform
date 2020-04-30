# -*- coding: utf-8 -*-

from datetime import datetime

from .. import db

bug_ass_baseline = db.Table(
    'bug_ass_baseline',
    db.Column('baseline_id',
              db.Integer,
              db.ForeignKey('baselines.id'),
              primary_key=True),
    db.Column('bug_id',
              db.Integer,
              db.ForeignKey('issue_bug.id'),
              primary_key=True))

requirement_ass_baseline = db.Table(
    'requirement_ass_baseline',
    db.Column('baseline_id',
              db.Integer,
              db.ForeignKey('baselines.id'),
              primary_key=True),
    db.Column('requirement_id',
              db.Integer,
              db.ForeignKey('issue_requirement.id'),
              primary_key=True))

task_ass_baseline = db.Table(
    'task_ass_baseline',
    db.Column('baseline_id',
              db.Integer,
              db.ForeignKey('baselines.id'),
              primary_key=True),
    db.Column('task_id',
              db.Integer,
              db.ForeignKey('issue_task.id'),
              primary_key=True))


# 问题来源： 1.Frog 2.禅道 3.Mantis  4.Jira
class IssueSource(db.Model):
    __tablename__ = 'issue_source'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True, index=True)

    requirements = db.relationship('IssueRequirement', back_populates='source')
    bugs = db.relationship('IssueBug', back_populates='source')


# 问题类别: 1.bug  2.需求  3.任务
class IssueCategory(db.Model):
    __tablename__ = 'issue_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True, index=True)
    baselines = db.relationship('Baseline', back_populates='issue_category')


# 问题模块: 1.再保 2.准备金 3.平台 4.承保 5.产品 6.报表 7.收付
# 8.理赔 9.财务 10.销售  11.自动任务 12.数据迁移
class IssueModule(db.Model):
    __tablename__ = 'issue_module'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True, index=True)

    requirements = db.relationship('IssueRequirement', back_populates='module')
    bugs = db.relationship('IssueBug', back_populates='module')


# 再现性： 1.不适用 2.总是 3.无法重现 4.有时 5.没有试验 6.随机
class IssueReproducibility(db.Model):
    __tablename__ = 'issue_reproducibility'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True, index=True)

    bugs = db.relationship('IssueBug', back_populates='reproducibility')


# 优先级: 1.中 2.低 3.无 4.紧急 5.高
class IssuePriority(db.Model):
    __tablename__ = 'issue_priority'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True, index=True)

    requirements = db.relationship('IssueRequirement',
                                   back_populates='priority')
    bugs = db.relationship('IssueBug', back_populates='priority')
    tasks = db.relationship('IssueTask', back_populates='priority')


# 严重程度: 1.宕机 2.小调整 3.小错误 4.崩溃 5.很严重 6.文字 7.新功能 8.细节
class IssueSeverity(db.Model):
    __tablename__ = 'issue_severity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True, index=True)
    bugs = db.relationship('IssueBug', back_populates='severity')


# 需求表
class IssueRequirement(db.Model):
    __tablename__ = 'issue_requirement'
    id = db.Column(db.Integer, primary_key=True)  # 需求编号
    number = db.Column(db.String(128))  # 需求原始编号
    reporter = db.Column(db.String(64))  # 报告人
    summary = db.Column(db.String(255), nullable=False)  # 摘要
    description = db.Column(db.Text)  # 详情
    inputdate = db.Column(db.DateTime(), default=datetime.now)  # 录入日期
    startdate = db.Column(db.DateTime())  # 开始日期
    enddate = db.Column(db.DateTime())  # 结束日期
    deadline = db.Column(db.DateTime(), default=datetime.now)  # 解决期限
    manhour = db.Column(db.String(64))  # 工时
    sign = db.Column(db.Boolean, default=False)  # 是否签字，默认为否

    status_id = db.Column(db.Integer, db.ForeignKey('status.id'),
                          default=101)  # 需求状态
    status = db.relationship('Status', back_populates='requirements')
    priority_id = db.Column(db.Integer,
                            db.ForeignKey('issue_priority.id'))  # 优先级
    priority = db.relationship('IssuePriority', back_populates='requirements')
    source_id = db.Column(db.Integer,
                          db.ForeignKey('issue_source.id'),
                          default=1)  # 需求来源
    source = db.relationship('IssueSource', back_populates='requirements')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # 所属项目
    project = db.relationship('Project', back_populates='requirements')
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 负责人
    assignee = db.relationship('User', back_populates='requirements')
    module_id = db.Column(db.Integer, db.ForeignKey('issue_module.id'))  # 模块
    module = db.relationship('IssueModule',
                             back_populates='requirements')  # 需求模块
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))  # 模块
    tag = db.relationship('Tag', back_populates='requirements')  # 标签

    baselines = db.relationship('Baseline',
                                secondary='requirement_ass_baseline',
                                back_populates='issue_requirements')  # 关联基线
    tasks = db.relationship('IssueTask',
                            back_populates='requirement')  # 需求分解的任务


# bug表
class IssueBug(db.Model):
    __tablename__ = 'issue_bug'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    number = db.Column(db.String(128))  # bug原始编号
    reporter = db.Column(db.String(64))  # 报告人
    summary = db.Column(db.String(255), nullable=False)  # 摘要
    description = db.Column(db.Text)  # 详情
    inputdate = db.Column(db.DateTime(), default=datetime.now)  # 录入日期
    startdate = db.Column(db.DateTime())  # 开始日期
    enddate = db.Column(db.DateTime())  # 结束日期
    deadline = db.Column(db.DateTime())  # 解决期限
    manhour = db.Column(db.String(64))  # 工时
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'),
                          default=101)  # bug状态
    status = db.relationship('Status', back_populates='bugs')
    priority_id = db.Column(db.Integer,
                            db.ForeignKey('issue_priority.id'))  # 优先级
    priority = db.relationship('IssuePriority', back_populates='bugs')
    severity_id = db.Column(db.Integer,
                            db.ForeignKey('issue_severity.id'))  # 严重性
    severity = db.relationship('IssueSeverity', back_populates='bugs')
    reproducibility_id = db.Column(
        db.Integer, db.ForeignKey('issue_reproducibility.id'))  # 再现性
    reproducibility = db.relationship('IssueReproducibility',
                                      back_populates='bugs')
    source_id = db.Column(db.Integer,
                          db.ForeignKey('issue_source.id'),
                          default=1)  # 来源
    source = db.relationship('IssueSource', back_populates='bugs')
    project_id = db.Column(db.Integer,
                           db.ForeignKey('projects.id'),
                           nullable=False)  # issue所属项目
    project = db.relationship('Project', back_populates='bugs')
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 负责人
    assignee = db.relationship('User', back_populates='bugs')
    module_id = db.Column(db.Integer, db.ForeignKey('issue_module.id'))  # 模块
    module = db.relationship('IssueModule', back_populates='bugs')  # 所属模块
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))  # 模块
    tag = db.relationship('Tag')  # 标签
    baselines = db.relationship('Baseline',
                                secondary='bug_ass_baseline',
                                back_populates='issue_bugs')


# 任务表,任务为需求的分解
class IssueTask(db.Model):
    __tablename__ = 'issue_task'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    number = db.Column(db.String(128))  # 任务原始编号
    summary = db.Column(db.String(255), nullable=False)  # 摘要
    description = db.Column(db.Text)  # 详情
    inputdate = db.Column(db.DateTime(), default=datetime.now)  # 录入日期
    startdate = db.Column(db.DateTime())  # 开始日期
    enddate = db.Column(db.DateTime())  # 结束日期
    deadline = db.Column(db.DateTime())  # 解决期限
    manhour = db.Column(db.String(64))  # 工时

    project_id = db.Column(db.Integer,
                           db.ForeignKey('projects.id'),
                           nullable=False)  # issue所属项目
    project = db.relationship('Project', back_populates='tasks')
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'),
                          default=101)  # 状态
    status = db.relationship('Status', back_populates='tasks')
    requirement_id = db.Column(db.Integer,
                               db.ForeignKey('issue_requirement.id'))  # 所属需求
    requirement = db.relationship('IssueRequirement', back_populates='tasks')
    assignee_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            nullable=False)  # 分配到任务的人
    assignee = db.relationship('User', back_populates='tasks')
    priority_id = db.Column(db.Integer,
                            db.ForeignKey('issue_priority.id'))  # 优先级
    priority = db.relationship('IssuePriority', back_populates='tasks')
    baselines = db.relationship('Baseline',
                                secondary='task_ass_baseline',
                                back_populates='issue_tasks')
