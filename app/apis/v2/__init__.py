#-*- coding: UTF-8 -*-
from flask import Blueprint
from flask_rest_jsonapi import Api

from app import  flask_app
from app.apis.v2.auth import auth_required
from .permission import permission_manager


api_v2 = Blueprint('api_v2', __name__)
# from app.apis.v2 import resources
#api = Api(flask_app,decorators=(auth_required,))
api = Api(flask_app)
api.init_app(flask_app)
from .resources import auth, cmdb, service, vcs, issues
#　权限控制
from .resources.baseconfig import StatusList, StatusDetail
from .resources.auth import ProjectList,ProjectDetail,UserList,UserDetail,RoleList,RoleDetail
from .resources.cmdb import MachineList,MachineDetail,CredenceList,CredenceDetail,AgreementList,AgreementDetail
from .resources.service import DatabaseList,DatabaseDetail,SchemaList,SchemaDetail,EnvList,EnvDetail,SubsystemList,SubsystemDetail,AppList,AppDetail
from .resources.vcs import BaselineList,BaselineDetail


api.resource_registry = [
    ProjectList,ProjectDetail,UserList,UserDetail,RoleList,RoleDetail,
    MachineList,MachineDetail,CredenceList,CredenceDetail,AgreementList,AgreementDetail,
    DatabaseList,DatabaseDetail,SchemaList,SchemaDetail,EnvList,EnvDetail,SubsystemList,SubsystemDetail,AppList,AppDetail,
    BaselineList,BaselineDetail,StatusList,StatusDetail
]
api.permission_manager(permission_manager)

