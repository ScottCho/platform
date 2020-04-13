# -*- coding: utf-8 -*-
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

# 状态
class StatusSchema(Schema):
    class Meta:
        type_ = 'status'
        self_view = 'status_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'status_list'
        
    id = fields.Integer(dump_only=True)
    name = fields.Str()

    requirements = Relationship(self_view='status_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_requirement_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='issue_requirement')
    
    bugs = Relationship(self_view='status_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_bug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='issue_bug')
    
    baselines = Relationship(self_view='status_baselines',
                           self_view_kwargs={'id': '<id>'},
                           related_view='baseline_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='BaselineSchema',
                           type_='baseline') 


# 标签
class TagSchema(Schema):
    class Meta:
        type_ = 'tag'
        self_view = 'tag_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'tag_list'
        
    id = fields.Integer(dump_only=True)
    name = fields.Str()

    requirements = Relationship(self_view='tag_requirements',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_requirement_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueRequirementSchema',
                           type_='issue_requirement')
    
    bugs = Relationship(self_view='tag_bugs',
                           self_view_kwargs={'id': '<id>'},
                           related_view='issue_bug_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='IssueBugSchema',
                           type_='issue_bug')  