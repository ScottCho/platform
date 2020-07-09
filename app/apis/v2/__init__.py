# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask_rest_jsonapi import Api

from app import flask_app

from .permission import permission_manager


api_v2 = Blueprint('api_v2', __name__)
api = Api(flask_app)
api.init_app(flask_app)


# 权限控制
from .resources import auth, cmdb, issues, service, stat, vcs
from .resources.auth import (ProjectDetail, ProjectList, RoleDetail, RoleList,
                             UserDetail, UserList)
from .resources.baseconfig import StatusDetail, StatusList
from .resources.cmdb import (AgreementDetail, AgreementList, CredenceDetail,
                             CredenceList, ServerDetail, ServerList)
from .resources.issues import (IssueBugDetail, IssueBugList,
                               IssueCategoryDetail, IssueCategoryList,
                               IssueModuleDetail, IssueModuleList,
                               IssuePriorityDetail, IssuePriorityList,
                               IssueReproducibilityDetail,
                               IssueReproducibilityList,
                               IssueRequirementDetail, IssueRequirementList,
                               IssueSeverityDetail, IssueSeverityList,
                               IssueSourceDetail, IssueSourceList,
                               IssueTaskDetail, IssueTaskList, UploadIssueAPI)
from .resources.service import (AppDetail, AppList, DatabaseDetail, AppReleaseDetail, 
                                DatabaseList, EnvDetail, EnvList, SchemaDetail,
                                SchemaList, SubsystemDetail, SubsystemList)
from .resources.vcs import (BaselineDetail, BaselineList,
                            PackageDetail, PackageList)
from .resources.account import svn_user_create
from .views.subversion import repo

# 注册后才可以进行权限控制
api.resource_registry = [
    ProjectList, ProjectDetail, UserList, UserDetail, RoleList, RoleDetail,
    ServerList, ServerDetail, CredenceList, CredenceDetail, AgreementList,
    AgreementDetail, DatabaseList, DatabaseDetail, SchemaList, SchemaDetail,
    EnvList, EnvDetail, SubsystemList, SubsystemDetail, AppList, AppDetail,
    BaselineList, BaselineDetail, StatusList, StatusDetail, AppReleaseDetail,
    PackageDetail, PackageList,
    IssueBugDetail, IssueBugList,
    IssueCategoryDetail, IssueCategoryList,
    IssueModuleDetail, IssueModuleList,
    IssuePriorityDetail, IssuePriorityList,
    IssueReproducibilityDetail,
    IssueReproducibilityList,
    IssueRequirementDetail, IssueRequirementList,
    IssueSeverityDetail, IssueSeverityList,
    IssueSourceDetail, IssueSourceList,
    IssueTaskDetail, IssueTaskList, UploadIssueAPI
]
api.permission_manager(permission_manager)
