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
api.route(IssueSourceList, 'isource_list', '/api/isources')
api.route(IssueSourceDetail, 'isource_detail', '/api/isources/<id>')
api.route(IssueSourceRelationship, 'isource_requirements', '/api/isources/<int:id>/relationships/requirements')
api.route(IssueSourceRelationship, 'isource_bugs', '/api/isources/<int:id>/relationships/bugs')

# 问题模块
api.route(IssueModuleList, 'imodule_list', '/api/imodules')
api.route(IssueModuleDetail, 'imodule_detail', '/api/imodule/<id>')
api.route(IssueModuleRelationship, 'imodule_requirements', '/api/imodule/<int:id>/relationships/requirements')
api.route(IssueModuleRelationship, 'imodule_bugs', '/api/imodule/<int:id>/relationships/bugs')

# 问题再现性
api.route(IssueReproducibilityList, 'ireproducibility_list', '/api/ireproducibility')
api.route(IssueReproducibilityDetail, 'ireproducibility_detail', '/api/ireproducibility/<id>')
api.route(IssueReproducibilityRelationship, 'ireproducibility_bugs', '/api/ireproducibility/<int:id>/relationships/bugs')

#　问题严重性
api.route(IssueSeverityList, 'iseverity_list', '/api/iseverity')
api.route(IssueSeverityDetail, 'iseverity_detail', '/api/iseverity/<id>')
api.route(IssueSeverityRelationship, 'iseverity_bugs', '/api/iseverity/<int:id>/relationships/bugs')

#　问题状态
api.route(IssueStatusList, 'istatus_list', '/api/istatus')
api.route(IssueStatusDetail, 'istatus_detail', '/api/istatus/<id>')
api.route(IssueStatusRelationship, 'istatus_requirements', '/api/istatus/<int:id>/relationships/requirements')
api.route(IssueStatusRelationship, 'istatus_bugs', '/api/istatus/<int:id>/relationships/bugs')
api.route(IssueStatusRelationship, 'istatus_tasks', '/api/istatus/<int:id>/relationships/tasks')

# 问题标签
api.route(IssueTagList, 'itag_list', '/api/itags')
api.route(IssueTagDetail, 'itag_detail', '/api/itags/<id>')
api.route(IssueTagRelationship, 'itag_requirements', '/api/itag/<int:id>/relationships/requirements')
api.route(IssueTagRelationship, 'itag_bugs', '/api/itag/<int:id>/relationships/bugs')
api.route(IssueTagRelationship, 'itag_tasks', '/api/itag/<int:id>/relationships/tasks')

# 问题优先级
api.route(IssuePriorityList, 'ipriority_list', '/api/ipriority')
api.route(IssuePriorityDetail, 'ipriority_detail', '/api/ipriority/<id>')
api.route(IssuePriorityRelationship, 'ipriority_requirements', '/api/ipriority/<int:id>/relationships/requirements')
api.route(IssuePriorityRelationship, 'ipriority_bugs', '/api/ipriority/<int:id>/relationships/bugs')
api.route(IssuePriorityRelationship, 'ipriority_tasks', '/api/ipriority/<int:id>/relationships/tasks')

#　需求
api.route(IssueRequirementList, 'irequirement_list', '/api/irequirements')
api.route(IssueRequirementDetail, 'irequirement_detail', '/api/irequirements/<id>')
api.route(IssueRequirementRelationship, 'irequirement_tasks', '/api/irequirements/<int:id>/relationships/tasks')
api.route(IssueRequirementRelationship, 'irequirement_status', '/api/irequirements/<int:id>/relationships/status')
api.route(IssueRequirementRelationship, 'irequirement_baselines', '/api/irequirements/<int:id>/relationships/baselines')

# task
api.route(IssueTaskList, 'itask_list', '/api/itasks')
api.route(IssueTaskDetail, 'itask_detail', '/api/itasks/<id>')
api.route(IssueTaskRelationship, 'itask_status', '/api/itasks/<int:id>/relationships/status')
api.route(IssueTaskRelationship, 'itask_requirement', '/api/itasks/<int:id>/relationships/requirement')
api.route(IssueTaskRelationship, 'itask_baselines', '/api/itasks/<int:id>/relationships/baselines')



# bug
api.route(IssueBugList, 'ibug_list', '/api/ibugs')
api.route(IssueBugDetail, 'ibug_detail', '/api/ibugs/<id>')
api.route(IssueBugRelationship, 'ibug_status', '/api/ibugs/<int:id>/relationships/status')
api.route(IssueRequirementRelationship, 'ibug_baselines', '/api/ibugs/<int:id>/relationships/baselines')

