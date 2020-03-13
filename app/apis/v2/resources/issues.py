# -*- coding: utf-8 -*-

from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from flask_rest_jsonapi.querystring import QueryStringManager as QSManager
from werkzeug.wrappers import Response
from flask import request, url_for, make_response, redirect
from flask.wrappers import Response as FlaskResponse
from flask.views import MethodView, MethodViewType
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from marshmallow import ValidationError

from flask_rest_jsonapi.pagination import add_pagination_links
from flask_rest_jsonapi.exceptions import InvalidType, BadRequest, RelationNotFound
from flask_rest_jsonapi.decorators import check_headers, check_method_requirements, jsonapi_exception_formatter
from flask_rest_jsonapi.schema import compute_schema, get_relationships, get_model_field
from flask_rest_jsonapi.data_layers.base import BaseDataLayer
from flask_rest_jsonapi.data_layers.alchemy import SqlalchemyDataLayer
from flask_rest_jsonapi.utils import JSONEncoder

from  app import flask_app
from app.models.issues import IssueBug, IssueCategory, IssuePriority, IssueReproducibility, IssueModule, \
     IssueRequirement, IssueSeverity, IssueSource, IssueStatus, IssueTag, IssueTask

from app import db

from app.apis.v2 import api
from app.apis.v2.schemas.issues import IssueBugSchema, IssueModuleSchema, IssuePrioritySchema, IssueReproducibilitySchema, \
    IssueRequirementSchema, IssueSeveritySchema, IssueSourceSchema, IssueStatusSchema, IssueTagSchema, IssueTaskSchema

from flask import jsonify, request, current_app, url_for, g
from flask.views import MethodView

from app.apis.v2 import api_v2
from app.apis.v2.auth import auth_required, generate_token, get_token
from app.apis.v2.errors import api_abort, ValidationError
from app.models.auth import User
from app.localemail import send_email
from flask_rest_jsonapi.exceptions import AccessDenied, JsonApiException

# Create resource managers
# 问题来源
class IssueSourceList(ResourceList):

    decorators = (auth_required,)
    schema = IssueSourceSchema
    data_layer = {'session': db.session,
                  'model': IssueSource
                }

class IssueSourceDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueSourceSchema
    data_layer = {'session': db.session,
                  'model': IssueSource  
                }

class IssueSourceRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueSourceSchema
    data_layer = {'session': db.session,
                  'model': IssueSource}

#　问题模块
class IssueModuleList(ResourceList):
    
    decorators = (auth_required,)
    schema = IssueModuleSchema
    data_layer = {'session': db.session,
                  'model': IssueModule
                }

class IssueModuleDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueModuleSchema
    data_layer = {'session': db.session,
                  'model': IssueModule 
                }

class IssueModuleRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueModuleSchema
    data_layer = {'session': db.session,
                  'model': IssueModule
                  }


# 问题再现性
class IssueReproducibilityList(ResourceList):
    
    decorators = (auth_required,)
    schema = IssueReproducibilitySchema
    data_layer = {'session': db.session,
                  'model': IssueReproducibility
                }

class IssueReproducibilityDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueReproducibilitySchema
    data_layer = {'session': db.session,
                  'model': IssueReproducibility 
                }

class IssueReproducibilityRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueReproducibilitySchema
    data_layer = {'session': db.session,
                  'model': IssueReproducibility
                  }


# 问题严重性
class IssueSeverityList(ResourceList):
    
    decorators = (auth_required,)
    schema = IssueSeveritySchema
    data_layer = {'session': db.session,
                  'model': IssueSeverity
                }

class IssueSeverityDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueSeveritySchema
    data_layer = {'session': db.session,
                  'model': IssueSeverity
                }

class IssueSeverityRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueSeveritySchema
    data_layer = {'session': db.session,
                  'model': IssueSeverity
                  }

# 问题状态
class IssueStatusList(ResourceList):
    
    decorators = (auth_required,)
    schema = IssueStatusSchema
    data_layer = {'session': db.session,
                  'model': IssueStatus
                }

class IssueStatusDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueStatusSchema
    data_layer = {'session': db.session,
                  'model': IssueStatus  
                }

class IssueStatusRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueStatusSchema
    data_layer = {'session': db.session,
                  'model': IssueStatus}

#　问题标签
class IssueTagList(ResourceList):
    
    decorators = (auth_required,)
    schema = IssueTagSchema
    data_layer = {'session': db.session,
                  'model': IssueTag
                }

class IssueTagDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueTagSchema
    data_layer = {'session': db.session,
                  'model': IssueTag 
                }

class IssueTagRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueTagSchema
    data_layer = {'session': db.session,
                  'model': IssueTag
                  }


#　问题优先级
class IssuePriorityList(ResourceList):
    
    decorators = (auth_required,)
    schema = IssuePrioritySchema
    data_layer = {'session': db.session,
                  'model': IssuePriority
                }

class IssuePriorityDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssuePrioritySchema
    data_layer = {'session': db.session,
                  'model': IssuePriority
                }

class IssuePriorityRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssuePrioritySchema
    data_layer = {'session': db.session,
                  'model': IssuePriority
                  }

# 需求
class IssueRequirementList(ResourceList):
    
    decorators = (auth_required,)
    def before_post(self, args, kwargs, data=None):
        pass

    schema = IssueRequirementSchema
    data_layer = {'session': db.session,
                  'model': IssueRequirement
                }

class IssueRequirementDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueRequirementSchema
    data_layer = {'session': db.session,
                  'model': IssueRequirement
                }

class IssueRequirementRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueRequirementSchema
    data_layer = {'session': db.session,
                  'model': IssueRequirement
                  }


# 任务
class IssueTaskList(ResourceList):
    
    decorators = (auth_required,)
    schema = IssueTaskSchema
    data_layer = {'session': db.session,
                  'model': IssueTask
                }

class IssueTaskDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueTaskSchema
    data_layer = {'session': db.session,
                  'model': IssueTask
                }

class IssueTaskRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueTaskSchema
    data_layer = {'session': db.session,
                  'model': IssueTask
                  }


# Bug
class IssueBugList(ResourceList):
    
    decorators = (auth_required,)
    schema =IssueBugSchema
    data_layer = {'session': db.session,
                  'model': IssueBug
                }

class IssueBugDetail(ResourceDetail):
    decorators = (auth_required,)

    schema = IssueBugSchema
    data_layer = {'session': db.session,
                  'model': IssueBug
                }

class IssueBugRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = IssueBugSchema
    data_layer = {'session': db.session,
                  'model': IssueBug
                  }

# Create endpoints
# 问题来源
api.route(IssueSourceList, 'issue_source_list', '/api/issue_sources')
api.route(IssueSourceDetail, 'issue_source_detail', '/api/issue_sources/<id>')
api.route(IssueSourceRelationship, 'issue_source_requirements', '/api/issue_sources/<int:id>/relationships/issue_requirements')
api.route(IssueSourceRelationship, 'issue_source_bugs', '/api/issue_sources/<int:id>/relationships/issue_bugs')

# 问题模块
api.route(IssueModuleList, 'issue_module_list', '/api/issue_modules')
api.route(IssueModuleDetail, 'issue_module_detail', '/api/issue_module/<id>')
api.route(IssueModuleRelationship, 'issue_module_requirements', '/api/issue_module/<int:id>/relationships/issue_requirements')
api.route(IssueModuleRelationship, 'issue_module_bugs', '/api/issue_module/<int:id>/relationships/issue_bugs')

# 问题再现性
api.route(IssueReproducibilityList, 'issue_reproducibility_list', '/api/issue_reproducibility')
api.route(IssueReproducibilityDetail, 'issue_reproducibility_detail', '/api/issue_reproducibility/<id>')
api.route(IssueReproducibilityRelationship, 'issue_reproducibility_bugs', '/api/issue_reproducibility/<int:id>/relationships/issue_bugs')

#　问题严重性
api.route(IssueSeverityList, 'issue_severity_list', '/api/issue_severity')
api.route(IssueSeverityDetail, 'issue_severity_detail', '/api/issue_severity/<id>')
api.route(IssueSeverityRelationship, 'issue_severity_bugs', '/api/issue_severity/<int:id>/relationships/issue_bugs')

#　问题状态
api.route(IssueStatusList, 'issue_status_list', '/api/issue_status')
api.route(IssueStatusDetail, 'issue_status_detail', '/api/issue_status/<id>')
api.route(IssueStatusRelationship, 'issue_status_requirements', '/api/issue_status/<int:id>/relationships/issue_requirements')
api.route(IssueStatusRelationship, 'issue_status_bugs', '/api/issue_status/<int:id>/relationships/issue_bugs')
api.route(IssueStatusRelationship, 'issue_status_tasks', '/api/issue_status/<int:id>/relationships/issue_tasks')

# 问题标签
api.route(IssueTagList, 'issue_tag_list', '/api/issue_tags')
api.route(IssueTagDetail, 'issue_tag_detail', '/api/issue_tags/<id>')
api.route(IssueTagRelationship, 'issue_tag_requirements', '/api/issue_tag/<int:id>/relationships/issue_requirements')
api.route(IssueTagRelationship, 'issue_tag_bugs', '/api/issue_tag/<int:id>/relationships/issue_bugs')
api.route(IssueTagRelationship, 'issue_tag_tasks', '/api/issue_tag/<int:id>/relationships/issue_tasks')

# 问题优先级
api.route(IssuePriorityList, 'issue_priority_list', '/api/issue_priority')
api.route(IssuePriorityDetail, 'issue_priority_detail', '/api/issue_priority/<id>')
api.route(IssuePriorityRelationship, 'issue_priority_requirements', '/api/issue_priority/<int:id>/relationships/issue_requirements')
api.route(IssuePriorityRelationship, 'issue_priority_bugs', '/api/issue_priority/<int:id>/relationships/issue_bugs')
api.route(IssuePriorityRelationship, 'issue_priority_tasks', '/api/issue_priority/<int:id>/relationships/issue_tasks')

#　需求
api.route(IssueRequirementList, 'issue_requirement_list', '/api/issue_requirements')
api.route(IssueRequirementDetail, 'issue_requirement_detail', '/api/issue_requirements/<id>')
api.route(IssueRequirementRelationship, 'issue_requirement_tasks', '/api/issue_requirements/<int:id>/relationships/issue_tasks')
api.route(IssueRequirementRelationship, 'issue_requirement_status', '/api/issue_requirements/<int:id>/relationships/issue_status')
api.route(IssueRequirementRelationship, 'issue_requirement_baselines', '/api/issue_requirements/<int:id>/relationships/baselines')

# task
api.route(IssueTaskList, 'issue_task_list', '/api/issue_tasks')
api.route(IssueTaskDetail, 'issue_task_detail', '/api/issue_tasks/<id>')
api.route(IssueTaskRelationship, 'issue_task_status', '/api/issue_tasks/<int:id>/relationships/issue_status')
api.route(IssueTaskRelationship, 'issue_task_requirement', '/api/issue_tasks/<int:id>/relationships/issue_requirement')
api.route(IssueTaskRelationship, 'issue_task_baselines', '/api/issue_tasks/<int:id>/relationships/baselines')



# bug
api.route(IssueBugList, 'issue_bug_list', '/api/issue_bugs')
api.route(IssueBugDetail, 'issue_bug_detail', '/api/issue_bugs/<id>')
api.route(IssueBugRelationship, 'issue_bug_status', '/api/issue_bugs/<int:id>/relationships/issue_status')
api.route(IssueRequirementRelationship, 'issue_bug_baselines', '/api/issue_bugs/<int:id>/relationships/baselines')

