# -*- coding: utf-8 -*-
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

# Create logical data abstraction
class IssueSourceSchema(Schema):
    class Meta:
        type_ = 'issue_source'
        self_view = 'issue_source_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_source_list'
        
    id = fields.Integer(dump_only=True)
    name = fields.Str()

    requirements = Relationship(self_view='issue_source_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_requirement_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='issue_requirement')
    
    bugs = Relationship(self_view='issue_source_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_bug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='issue_bug')  
                           

# 模块
class IssueModuleSchema(Schema):
    class Meta:
        type_ = 'issue_module'
        self_view = 'issue_module_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_module_list'
        
    id = fields.Integer(dump_only=True)
    name = fields.Str()
    
    requirements = Relationship(self_view='issue_module_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_bug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='issue_requirement')
    
    bugs = Relationship(self_view='issue_module_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_bug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='issue_bug')  
                           

# 再现性
class IssueReproducibilitySchema(Schema):
    class Meta:
        type_ = 'issue_reproducibility'
        self_view = 'issue_reproducibility_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_reproducibility_list'
        
    id = fields.Integer(dump_only=True)
    name = fields.Str()
    
    bugs = Relationship(self_view='issue_reproducibility_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_bug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='issue_bug')  

# 优先级
class IssuePrioritySchema(Schema):
    class Meta:
        type_ = 'issue_priority'
        self_view = 'issue_priority_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_priority_list'
        
    id = fields.Integer(dump_only=True)
    name = fields.Str()
    
    bugs = Relationship(self_view='issue_priority_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_bug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='issue_bug')  

    requirements = Relationship(self_view='issue_priority_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_requirement_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='issue_requirement')

    tasks = Relationship(self_view='issue_priority_tasks',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_task_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueTaskSchema',
                           type_='issue_task') 
# 严重性
class IssueSeveritySchema(Schema):
    class Meta:
        type_ = 'issue_severity'
        self_view = 'issue_severity_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_severity_list'
        
    id = fields.Integer(dump_only=True)
    name = fields.Str()

    bugs = Relationship(self_view='issue_severity_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_bug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='issue_bug')  


# 问题类别
class IssueCategorySchema(Schema):
    class Meta:
        type_ = 'issue_category'
        self_view = 'issue_category_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_category_list'
        
    id = fields.Integer(dump_only=True)
    name = fields.Str()

    baselines = Relationship(self_view='issue_category_baselines',
                           self_view_kwargs={'id': '<id>'},
                           related_view='baseline_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='BaselineSchema',
                           type_='baseline')  

# 需求
class IssueRequirementSchema(Schema):
    class Meta:
        type_ = 'issue_requirement'
        self_view = 'issue_requirement_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_requirement_list'
        
    id = fields.Integer(dump_only=True)
    number = fields.Str(allow_none=True)
    reporter = fields.Str(allow_none=True)
    summary = fields.Str()
    description = fields.Str(allow_none=True)
    inputdate = fields.Date(allow_none=True)
    startdate = fields.Date(allow_none=True)
    enddate = fields.Date(allow_none=True)
    deadline = fields.Date(allow_none=True)
    manhour = fields.Str(allow_none=True)
    sign = fields.Bool()
    status_id = fields.Integer(default=101)
    status_name = fields.Function(lambda obj: "{}".format(obj.status.name))  
    priority_id = fields.Integer(allow_none=True)
    priority = fields.Function(lambda obj: "{}".format(obj.priority.name))
    source_id = fields.Integer(allow_none=True)
    source = fields.Function(lambda obj: "{}".format(obj.source.name))
    project_id = fields.Integer()
    project_name = fields.Function(lambda obj: "{}".format(obj.project.name))
    assignee_id = fields.Integer(allow_none=True)
    assignee = fields.Function(lambda obj: "{}".format(obj.assignee.username))
    module_id = fields.Integer(allow_none=True)
    module =  fields.Function(lambda obj: "{}".format(obj.module.name))
    tag_id = fields.Integer(allow_none=True)
    tag = fields.Function(lambda obj: "{}".format(obj.tag.name))

    tasks = Relationship(self_view='issue_requirement_tasks',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_task_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueTaskSchema',
                           type_='issue_task')
    
    baselines = Relationship(self_view='issue_requirement_baselines',
                             self_view_kwargs={'id': '<id>'},
                             related_view='baseline_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='BaselineSchema',
                             type_='baseline')


class IssueBugSchema(Schema):
    class Meta:
        type_ = 'issue_bug'
        self_view = 'issue_bug_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_bug_list'
        
    id = fields.Integer(dump_only=True)
    number = fields.Str(allow_none=True)
    reporter = fields.Str(allow_none=True)
    summary = fields.Str()
    description = fields.Str(allow_none=True)
    inputdate = fields.Date(allow_none=True)
    startdate = fields.Date(allow_none=True)
    enddate = fields.Date(allow_none=True)
    deadline = fields.Date(allow_none=True)
    manhour = fields.Str(allow_none=True)
    status_id = fields.Integer(allow_none=True)
    status_name = fields.Function(lambda obj: "{}".format(obj.status.name))
    priority_id = fields.Integer(allow_none=True)
    priority = fields.Function(lambda obj: "{}".format(obj.priority.name))
    severity_id = fields.Integer(allow_none=True)
    severity = fields.Function(lambda obj: "{}".format(obj.severity.name))
    reproducibility_id = fields.Integer()
    reproducibility = fields.Function(lambda obj: "{}".format(obj.reproducibility.name))
    project_id = fields.Integer()
    project_name = fields.Function(lambda obj: "{}".format(obj.project.name))
    assignee_id =  fields.Integer()
    assignee = fields.Function(lambda obj: "{}".format(obj.assignee.username))
    module_id =  fields.Integer(allow_none=True)
    module =  fields.Function(lambda obj: "{}".format(obj.module.name)) 
    tag_id =  fields.Integer(allow_none=True)
    tag = fields.Function(lambda obj: "{}".format(obj.tag.name))
    source_id = fields.Integer(allow_none=True)
    source = fields.Function(lambda obj: "{}".format(obj.source.name)) 
    baseline_id =  fields.Integer()

    baselines = Relationship(self_view='issue_bug_baselines',
                             self_view_kwargs={'id': '<id>'},
                             related_view='baseline_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='BaselineSchema',
                             type_='baseline')

    # assignee = Relationship(self_view='ibug_assignee',
    #                     self_view_kwargs={'id': '<id>'},
    #                     related_view='user_detail',
    #                     related_view_kwargs={'id': '<id>'},
    #                     schema='UserSchema',
    #                     type_='user')                    


class IssueTaskSchema(Schema):
    class Meta:
        type_ = 'issue_task'
        self_view = 'issue_task_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'issue_task_list'
        
    id = fields.Integer(dump_only=True)
    requirement_id = fields.Integer(allow_none=True)
    number = fields.Str(allow_none=True)
    reporter = fields.Str(allow_none=True)
    summary = fields.Str()
    description = fields.Str(allow_none=True)
    inputdate = fields.Date(allow_none=True)
    startdate = fields.Date(allow_none=True)
    enddate = fields.Date(allow_none=True)
    deadline = fields.Date(allow_none=True)
    manhour = fields.Str(allow_none=True)
    status_id = fields.Integer(allow_none=True)
    status_name = fields.Function(lambda obj: "{}".format(obj.status.name))
    priority_id = fields.Integer()
    priority = fields.Function(lambda obj: "{}".format(obj.priority.name))  
    assignee_id =  fields.Integer()
    assignee = fields.Function(lambda obj: "{}".format(obj.assignee.username))
    project_id = fields.Integer()
    project_name = fields.Function(lambda obj: "{}".format(obj.project.name))
    

    baselines = Relationship(self_view='issue_task_baselines',
                             self_view_kwargs={'id': '<id>'},
                             related_view='baseline_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='BaselineSchema',
                             type_='baseline')
    
    requirement = Relationship(self_view='issue_task_requirement',
                        self_view_kwargs={'id': '<id>'},
                        related_view='issue_requirement_detail',
                        related_view_kwargs={'id': '<id>'},
                        schema='IssueRequirementSchema',
                        type_='issue_requirement')