# -*- coding: utf-8 -*-
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

# Create logical data abstraction
class IssueSourceSchema(Schema):
    class Meta:
        type_ = 'isource'
        self_view = 'isource_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'isource_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()

    requirements = Relationship(self_view='isource_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='irequirement_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='irequirement')
    
    bugs = Relationship(self_view='isource_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='ibug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='ibug')  
                           

# 模块
class IssueModuleSchema(Schema):
    class Meta:
        type_ = 'imodule'
        self_view = 'imodule_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'imodule_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()
    
    requirements = Relationship(self_view='imodule_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='ibug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='irequirement')
    
    bugs = Relationship(self_view='imodule_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='ibug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='ibug')  
                           

# 再现性
class IssueReproducibilitySchema(Schema):
    class Meta:
        type_ = 'ireproducibility'
        self_view = 'ireproducibility_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'ireproducibility_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()
    
    bugs = Relationship(self_view='ireproducibility_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='ibug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='ibug')  

# 优先级
class IssuePrioritySchema(Schema):
    class Meta:
        type_ = 'ipriority'
        self_view = 'ipriority_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'ipriority_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()
    
    bugs = Relationship(self_view='ipriority_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='ibug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='ibug')  

    requirements = Relationship(self_view='ipriority_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='irequirement_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='irequirement')

# 严重性
class IssueSeveritySchema(Schema):
    class Meta:
        type_ = 'iseverity'
        self_view = 'iseverity_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'iseverity_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()

    bugs = Relationship(self_view='iseverity_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='ibug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='ibug')  


# 状态
class IssueStatusSchema(Schema):
    class Meta:
        type_ = 'istatus'
        self_view = 'istatus_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'istatus_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()

    requirements = Relationship(self_view='istatus_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='irequirement_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='irequirement')
    
    bugs = Relationship(self_view='istatus_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='ibug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='ibug')  


# 标签
class IssueTagSchema(Schema):
    class Meta:
        type_ = 'itag'
        self_view = 'itag_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'itag_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()

    requirements = Relationship(self_view='itag_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='irequirement_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='irequirement')
    
    bugs = Relationship(self_view='itag_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='ibug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='ibug')  


# 需求
class IssueRequirementSchema(Schema):
    class Meta:
        type_ = 'irequirement'
        self_view = 'irequirement_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'irequirement_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    number = fields.Str()
    reporter = fields.Str()
    summary = fields.Str()
    description = fields.Str()
    inputdate = fields.Date()
    startdate = fields.Date()
    enddate = fields.Date()
    deadline = fields.Date()
    manhour = fields.Str()
    sign = fields.Bool()
    status_id = fields.Integer()
    status = fields.Function(lambda obj: "{}".format(obj.status.name))  
    priority_id = fields.Integer()
    priority = fields.Function(lambda obj: "{}".format(obj.priority.name))
    source_id = fields.Integer()
    source = fields.Function(lambda obj: "{}".format(obj.source.name))
    project_id = fields.Integer()
    project = fields.Function(lambda obj: "{}".format(obj.project.name))
    assignee_id = fields.Integer()
    assignee = fields.Function(lambda obj: "{}".format(obj.assignee.username))
    module_id = fields.Integer()
    module =  fields.Function(lambda obj: "{}".format(obj.module.name))
    tag_id = fields.Integer()
    tag = fields.Function(lambda obj: "{}".format(obj.tag.name))

    tasks = Relationship(self_view='irequirement_tasks',
                           self_view_kwargs={'id': '<id>'},
                           related_view='itask_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueTaskSchema',
                           type_='itask')
    
    baselines = Relationship(self_view='irequirement_baselines',
                             self_view_kwargs={'id': '<id>'},
                             related_view='baseline_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='BaselineSchema',
                             type_='baseline')


class IssueBugSchema(Schema):
    class Meta:
        type_ = 'ibug'
        self_view = 'ibug_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'ibug_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    number = fields.Str()
    reporter = fields.Str()
    summary = fields.Str()
    description = fields.Str()
    inputdate = fields.Date()
    startdate = fields.Date()
    enddate = fields.Date()
    deadline = fields.Date()
    manhour = fields.Str()
    status_id = fields.Integer()
    status = fields.Function(lambda obj: "{}".format(obj.status.name))
    severity_id = fields.Integer()
    severity = fields.Function(lambda obj: "{}".format(obj.severity.name))
    reproducibility_id = fields.Integer()
    reproducibility = fields.Function(lambda obj: "{}".format(obj.reproducibility.name))
    project_id = fields.Integer()
    project = fields.Function(lambda obj: "{}".format(obj.project.name))
    assignee_id =  fields.Integer()
    assignee = fields.Function(lambda obj: "{}".format(obj.assignee.username))
    module_id =  fields.Integer()
    module =  fields.Function(lambda obj: "{}".format(obj.module.name)) 
    tag_id =  fields.Integer()
    tag = fields.Function(lambda obj: "{}".format(obj.tag.name)) 
    baseline_id =  fields.Integer()

    baselines = Relationship(self_view='ibug_baselines',
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
        type_ = 'itask'
        self_view = 'itask_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'itask_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()
    number = fields.Str()
    reporter = fields.Str()
    summary = fields.Str()
    description = fields.Str()
    inputdate = fields.Date()
    startdate = fields.Date()
    enddate = fields.Date()
    deadline = fields.Date()
    manhour = fields.Str()
    status_id = fields.Integer()
    status = fields.Function(lambda obj: "{}".format(obj.status.name))  
    assignee_id =  fields.Integer()
    assignee = fields.Function(lambda obj: "{}".format(obj.assignee.username))
    

    baselines = Relationship(self_view='itask_baselines',
                             self_view_kwargs={'id': '<id>'},
                             related_view='baseline_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='BaselineSchema',
                             type_='baseline')
    
    requirement = Relationship(self_view='itask_requirement',
                        self_view_kwargs={'id': '<id>'},
                        related_view='irequirement_detail',
                        related_view_kwargs={'id': '<id>'},
                        schema='IssueRequirementSchema',
                        type_='irequirement')