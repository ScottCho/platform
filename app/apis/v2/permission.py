from collections import ChainMap

from flask import request, g


from flask_rest_jsonapi.exceptions import AccessDenied, JsonApiException

# 默认权限
default={
        'baseline_list': {'post': False,  'get': True},
        'baseline_detail': {'patch': False, 'get': True, 'delete': False},
        'package_list': {'post': False,  'get': True},
        'package_detail': {'patch': False, 'get': True, 'delete': False},
        'package_merge': {'patch': False, 'get': False, 'delete': False},
        'package_deploy': {'patch': False, 'get': False, 'delete': False},
        'package_release': {'patch': False, 'get': False, 'delete': False},
        'project_list': {'post': False,'get': True},
        'project_detail': {'patch': False, 'get': True, 'delete': False},
        'user_list': {'post': False,  'get': True},
        'user_detail': {'patch': False, 'get': True, 'delete': False},
        'subsystem_list': {'post': False,  'get': False},
        'subsystem_detail': {'patch': False, 'get': False, 'delete': False},
        'schema_list': {'post': False,  'get': False},
        'schema_detail': {'patch': False, 'get': False, 'delete': False},
        'agreement_list': {'post': False,  'get': False},
        'agreement_detail': {'patch': False, 'get': False, 'delete': False},
        'app_list': {'post': False,  'get': True},
        'app_detail': {'patch': False, 'get': True, 'delete': False},
        'blstatus_list': {'post': False,  'get': True},
        'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
        'machine_list': {'post': False,  'get': False},
        'machine_detail': {'patch': False, 'get': False, 'delete': False},
        'role_list': {'post': False,  'get': True},
        'role_detail': {'patch': False, 'get': False, 'delete': False},
        'database_list': {'post': False,  'get': False},
        'database_detail': {'patch': False, 'get': False, 'delete': False},
        'env_list': {'post': False,  'get': True},
        'env_detail': {'patch': False, 'get': False, 'delete': False},
        'credence_list': {'post': False,  'get': False},
        'credence_detail': {'patch': False, 'get': False, 'delete': False},
        'issue_bug_detail':{'patch':False, 'get': True, 'delete':False},
        'issue_bug_list':{'post': False,  'get': True},
        'issue_module_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_module_list':{'post': False,  'get': True},
        'issue_priority_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_priority_list':{'post': False,  'get': True},
        'issue_reproducibility_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_reproducibility_list':{'post': False,  'get': True},
        'issue_requirement_list':{'post': False,  'get': True},
        'issue_requirements_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_severity_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_severity_list':{'post': False,  'get': True},
        'issue_source_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_source_list':{'post': False,  'get': True},
        'issue_status_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_status_list':{'post': False,  'get': True},
        'issue_tag_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_tag_list':{'post': False,  'get': True},
        'issue_task_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_task_list':{'post': False, 'get': True},
        'api_v2.confirm_user':{'get': True},
        'api_v2.password_change':{'post': True},
        'api_v2.password_reset':{'post': True, 'get': True},
        'api_v2.password_reset_request':{'get': True},
        'api_v2.register_user':{'post': True},
        'api_v2.token':{'post': True},
        'api_v2.token_user':{'get': True}
}

# 发布与更新基线
baseline_update={
    'baseline_list': {'post': True,  'get': True},
    'baseline_detail': {'patch': True, 'get': True, 'delete': False}
}

baseline_management={
    'baseline_list': {'post': True,  'get': True},
    'baseline_detail': {'patch': True, 'get': True, 'delete': True}
}

# 更新包发布
package_management={
        'package_list': {'post': True,  'get': True},
        'package_detail': {'patch': True, 'get': True, 'delete': True},
        'package_merge': {'patch': True, 'get': True, 'delete': True},
        'package_deploy': {'patch': True, 'get': True, 'delete': True},
        'package_release': {'patch': True, 'get': True, 'delete': True}
}

# 项目管理
project_management={
    'project_list': {'post': True,'get': True},
    'project_detail': {'patch': True, 'get': True, 'delete': True}
}

# 用户管理
user_management={
    'user_list': {'post': True,  'get': True},
    'user_detail': {'patch': True, 'get': True, 'delete': True}
}

# 角色管理
role_management={
    'role_list': {'post': True,  'get': True},
    'role_detail': {'patch': True, 'get': True, 'delete': True}
}

# CMDB
cmdb={
    'subsystem_list': {'post': True,  'get': True},
    'subsystem_detail': {'patch': True, 'get': True, 'delete': True},
    'schema_list': {'post': True,  'get': True},
    'schema_detail': {'patch': True, 'get': True, 'delete': True},
    'agreement_list': {'post': True,  'get': True},
    'agreement_detail': {'patch': True, 'get': True, 'delete': True},
    'machine_list': {'post': True,  'get': True},
    'machine_detail': {'patch': True, 'get': True, 'delete': True},
    'env_list': {'post': True,  'get': True},
    'env_detail': {'patch': True, 'get': True, 'delete': True},
    'credence_list': {'post': True,  'get': True},
    'credence_detail': {'patch': True, 'get': True, 'delete': True},
    'blstatus_list': {'post': True,  'get': True},
    'blstatus_detail': {'patch': True, 'get': True, 'delete': True}
}

# 服务管理
service_management={
    'database_list': {'post': True,  'get': True},
    'database_detail': {'patch': True, 'get': True, 'delete': True},
    'app_list': {'post': True,  'get': True},
    'app_detail': {'patch': True, 'get': True, 'delete': True}
}

# bug和任务管理，测试可以提交和关闭
bug_task_management = {
    'issue_bug_detail':{'patch':True, 'get': True, 'delete':True},
    'issue_bug_list':{'post': True,  'get': True},
    'issue_task_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_task_list':{'post': True, 'get': True}
}

# issue管理, 经理权限
issue_management = {
    'issue_requirement_list':{'post': True,  'get': True},
    'issue_requirements_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_bug_detail':{'patch':True, 'get': True, 'delete':True},
    'issue_bug_list':{'post': True,  'get': True},
    'issue_task_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_task_list':{'post': True, 'get': True}, 
    'issue_module_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_module_list':{'post': True,  'get': True},
    'issue_priority_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_priority_list':{'post': True,  'get': True},
    'issue_reproducibility_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_reproducibility_list':{'post': True,  'get': True},
    'issue_severity_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_severity_list':{'post': True,  'get': True},
    'issue_source_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_source_list':{'post': True,  'get': True},
    'issue_status_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_status_list':{'post': True,  'get': True},
    'issue_tag_detail':{'patch': True, 'get': True, 'delete': True},
    'issue_tag_list':{'post': True,  'get': True},  
}

Permission = {

    # 管理员
    'Administrator':ChainMap(baseline_management,package_management,project_management,
            user_management,role_management,cmdb,service_management,issue_management,default),

    # 开发
    'Developer':ChainMap(baseline_update,default),
    
    # 测试 
    'Tester':ChainMap(bug_task_management,default),

    # 经理  
    'Manager':ChainMap(issue_management,default),

    # 协管员
    'Moderator':ChainMap(package_management,baseline_management,service_management,default),

    # 运维
    'Operator':ChainMap(cmdb,service_management,package_management,default)
}   

def permission_manager(view, view_args, view_kwargs, *args, **kwargs):
    '''The function use to check permissions

    :param callable view: the view
    :param list view_args: view args
    :param dict view_kwargs: view kwargs
    :param list args: decorator args
    :param dict kwargs: decorator kwargs
    '''
    try:
        # 如果没有登录抛出异常
        role = g.current_user.role.name
    except:
        raise JsonApiException(detail='Unauthorized.',status=401)
    
    # request.endpoint=project_list   view.__name__=get
    if Permission.get(role,'Anonymous').get(request.endpoint).get(view.__name__) == False :
        raise AccessDenied(detail='Access Denied')

# Permission={
#     'Administrator':{
#         'baseline_list': {'post': True,  'get': True},
#         'baseline_detail': {'patch': True, 'get': True, 'delete': True},
#         'package_list': {'post': True,  'get': True},
#         'package_detail': {'patch': True, 'get': True, 'delete': True},
#         'package_merge': {'patch': True, 'get': True, 'delete': True},
#         'package_deploy': {'patch': True, 'get': True, 'delete': True},
#         'package_release': {'patch': True, 'get': True, 'delete': True},
#         'project_list': {'post': True,'get': True},
#         'project_detail': {'patch': True, 'get': True, 'delete': True},
#         'user_list': {'post': True,  'get': True},
#         'user_detail': {'patch': True, 'get': True, 'delete': True},
#         'subsystem_list': {'post': True,  'get': True},
#         'subsystem_detail': {'patch': True, 'get': True, 'delete': True},
#         'schema_list': {'post': True,  'get': True},
#         'schema_detail': {'patch': True, 'get': True, 'delete': True},
#         'agreement_list': {'post': True,  'get': True},
#         'agreement_detail': {'patch': True, 'get': True, 'delete': True},
#         'app_list': {'post': True,  'get': True},
#         'app_detail': {'patch': True, 'get': True, 'delete': True},
#         'blstatus_list': {'post': True,  'get': True},
#         'blstatus_detail': {'patch': True, 'get': True, 'delete': True},
#         'machine_list': {'post': True,  'get': True},
#         'machine_detail': {'patch': True, 'get': True, 'delete': True},
#         'role_list': {'post': True,  'get': True},
#         'role_detail': {'patch': True, 'get': True, 'delete': True},
#         'database_list': {'post': True,  'get': True},
#         'database_detail': {'patch': True, 'get': True, 'delete': True},
#         'env_list': {'post': True,  'get': True},
#         'env_detail': {'patch': True, 'get': True, 'delete': True},
#         'credence_list': {'post': True,  'get': True},
#         'credence_detail': {'patch': True, 'get': True, 'delete': True},
#         'issue_bug_detail':{'patch':True, 'get': True, 'delete':True},
#         'issue_bug_list':{'post': True,  'get': True},
#         'issue_module_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_module_list':{'post': True,  'get': True},
#         'issue_priority_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_priority_list':{'post': True,  'get': True},
#         'issue_reproducibility_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_reproducibility_list':{'post': True,  'get': True},
#         'issue_requirement_list':{'post': True,  'get': True},
#         'issue_requirements_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_severity_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_severity_list':{'post': True,  'get': True},
#         'issue_source_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_source_list':{'post': True,  'get': True},
#         'issue_status_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_status_list':{'post': True,  'get': True},
#         'issue_tag_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_tag_list':{'post': True,  'get': True},
#         'issue_task_detail':{'patch': True, 'get': True, 'delete': True},
#         'issue_task_list':{'post': True, 'get': True},
#     }, 
#     'Developer':{
#         'baseline_list': {'post': True,  'get': True},
#         'baseline_detail': {'patch': True, 'get': True, 'delete': False},
#         'package_list': {'post': False,  'get': True},
#         'package_detail': {'patch': False, 'get': True, 'delete': False},
#         'project_list': {'post': False,  'get': True},
#         'project_detail': {'patch': False, 'get': True, 'delete': False},
#         'package_merge': {'patch': False, 'get': False, 'delete': False},
#         'package_deploy':  {'patch': False, 'get': False, 'delete': False},
#         'package_release':  {'patch': False, 'get': False, 'delete': False},
#         'user_list': {'post': False,  'get': True},
#         'user_detail': {'patch': True, 'get': True, 'delete': False},
#         'subsystem_list': {'post': False,  'get': True},
#         'subsystem_detail': {'patch': False, 'get': True, 'delete': False},
#         'schema_list': {'post': False,  'get': False},
#         'schema_detail': {'patch': False, 'get': False, 'delete': False},
#         'agreement_list': {'post': False,  'get': False},
#         'agreement_detail': {'patch': False, 'get': False, 'delete': False},
#         'app_list': {'post': False,  'get': True},
#         'app_detail': {'patch': False, 'get': True, 'delete': False},
#         'blstatus_list': {'post': False,  'get': True},
#         'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
#         'machine_list': {'post': False,  'get': True},
#         'machine_detail': {'patch': False, 'get': True, 'delete': False},
#         'role_list': {'post': False,  'get': True},
#         'role_detail': {'patch': False, 'get': True, 'delete': False},
#         'database_list': {'post': False,  'get': True},
#         'database_detail': {'patch': False, 'get': True, 'delete': False},
#         'env_list': {'post': False,  'get': True},
#         'env_detail': {'patch': False, 'get': True, 'delete': False},
#         'credence_list': {'post': False,  'get': False},
#         'credence_detail': {'patch': False, 'get': False, 'delete': False},
#         'ibug_detail':{'patch': True, 'get': True, 'delete': False},
#         'ibug_list':{'post': True,  'get': True},
#         'imodule_detail':{'patch': False, 'get': True, 'delete': False},
#         'imodule_list':{'post': False,  'get': True},
#         'ipriority_detail':{'patch': False, 'get': True, 'delete': False},
#         'ipriority_list':{'post': False,  'get': True},
#         'ireproducibility_detail':{'patch': False, 'get': True, 'delete': False},
#         'ireproducibility_list':{'post': False,  'get': True},
#         'irequirement_list':{'post': False,  'get': True},
#         'irequirements_detail':{'patch': False, 'get': True, 'delete': False},
#         'iseverity_detail':{'patch': False, 'get': True, 'delete': False},
#         'iseverity_list':{'post': False,  'get': True},
#         'isource_detail':{'patch': False, 'get': True, 'delete': False},
#         'isource_list':{'post': False,  'get': True},
#         'istatus_detail':{'patch': False, 'get': True, 'delete': False},
#         'istatus_list':{'post': False,  'get': True},
#         'itag_detail':{'patch': False, 'get': True, 'delete': False},
#         'itag_list':{'post': False,  'get': True},
#         'itask_detail':{'patch': True, 'get': True, 'delete': False},
#         'itask_list':{'post': True, 'get': True}
#     },
#     'Tester':{
#         'baseline_list': {'post': False,  'get': True},
#         'baseline_detail': {'patch': False, 'get': True, 'delete': False},
#         'package_list': {'post': False,  'get': True},
#         'package_detail': {'patch': False, 'get': True, 'delete': False},
#         'package_merge': {'patch': False, 'get': False, 'delete': False},
#         'package_deploy':  {'patch': False, 'get': False, 'delete': False},
#         'package_release':  {'patch': False, 'get': False, 'delete': False},
#         'project_list': {'post': False,  'get': True},
#         'project_detail': {'patch': False, 'get': True, 'delete': False},
#         'user_list': {'post': False,  'get': True},
#         'user_detail': {'patch': True, 'get': True, 'delete': False},
#         'subsystem_list': {'post': False,  'get': True},
#         'subsystem_detail': {'patch': False, 'get': True, 'delete': False},
#         'schema_list': {'post': False,  'get': False},
#         'schema_detail': {'patch': False, 'get': False, 'delete': False},
#         'agreement_list': {'post': False,  'get': False},
#         'agreement_detail': {'patch': False, 'get': False, 'delete': False},
#         'app_list': {'post': False,  'get': True},
#         'app_detail': {'patch': False, 'get': True, 'delete': False},
#         'blstatus_list': {'post': False,  'get': True},
#         'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
#         'machine_list': {'post': False,  'get': True},
#         'machine_detail': {'patch': False, 'get': True, 'delete': False},
#         'role_list': {'post': False,  'get': True},
#         'role_detail': {'patch': False, 'get': True, 'delete': False},
#         'database_list': {'post': False,  'get': True},
#         'database_detail': {'patch': False, 'get': True, 'delete': False},
#         'env_list': {'post': False,  'get': True},
#         'env_detail': {'patch': False, 'get': True, 'delete': False},
#         'credence_list': {'post': False,  'get': False},
#         'credence_detail': {'patch': False, 'get': False, 'delete': False},
#         'ibug_detail':{'patch': True, 'get': True, 'delete': True},
#         'ibug_list':{'post': True,  'get': True},
#         'imodule_detail':{'patch': False, 'get': True, 'delete': False},
#         'imodule_list':{'post': False,  'get': True},
#         'ipriority_detail':{'patch': False, 'get': True, 'delete': False},
#         'ipriority_list':{'post': False,  'get': True},
#         'ireproducibility_detail':{'patch': False, 'get': True, 'delete': False},
#         'ireproducibility_list':{'post': False,  'get': True},
#         'irequirement_list':{'post': False,  'get': True},
#         'irequirements_detail':{'patch': False, 'get': True, 'delete': False},
#         'iseverity_detail':{'patch': False, 'get': True, 'delete': False},
#         'iseverity_list':{'post': False,  'get': True},
#         'isource_detail':{'patch': False, 'get': True, 'delete': False},
#         'isource_list':{'post': False,  'get': True},
#         'istatus_detail':{'patch': False, 'get': True, 'delete': False},
#         'istatus_list':{'post': False,  'get': True},
#         'itag_detail':{'patch': False, 'get': True, 'delete': False},
#         'itag_list':{'post': False,  'get': True},
#         'itask_detail':{'patch': False, 'get': True, 'delete': False},
#         'itask_list':{'post': False, 'get': True},
#     },
#     'Moderator':{
#         'baseline_list': {'post': True,  'get': True},
#         'baseline_detail': {'patch': True, 'get': True, 'delete': False},
#         'package_list': {'post': True,  'get': True},
#         'package_detail': {'patch': True, 'get': True, 'delete': False},
#         'package_merge': {'patch': False, 'get': True, 'delete': False},
#         'package_deploy':  {'patch': False, 'get': True, 'delete': False},
#         'package_release':  {'patch': False, 'get': True, 'delete': False},
#         'project_list': {'post': False,  'get': True},
#         'project_detail': {'patch': False, 'get': True, 'delete': False},
#         'user_list': {'post': False,  'get': True},
#         'user_detail': {'patch': True, 'get': True, 'delete': False},
#         'subsystem_list': {'post': False,  'get': True},
#         'subsystem_detail': {'patch': False, 'get': True, 'delete': False},
#         'schema_list': {'post': False,  'get': False},
#         'schema_detail': {'patch': False, 'get': False, 'delete': False},
#         'agreement_list': {'post': False,  'get': False},
#         'agreement_detail': {'patch': False, 'get': False, 'delete': False},
#         'app_list': {'post': False,  'get': True},
#         'app_detail': {'patch': False, 'get': True, 'delete': False},
#         'blstatus_list': {'post': False,  'get': True},
#         'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
#         'machine_list': {'post': False,  'get': True},
#         'machine_detail': {'patch': False, 'get': True, 'delete': False},
#         'role_list': {'post': False,  'get': True},
#         'role_detail': {'patch': False, 'get': True, 'delete': False},
#         'database_list': {'post': False,  'get': True},
#         'database_detail': {'patch': False, 'get': True, 'delete': False},
#         'env_list': {'post': False,  'get': True},
#         'env_detail': {'patch': False, 'get': True, 'delete': False},
#         'credence_list': {'post': False,  'get': False},
#         'credence_detail': {'patch': False, 'get': False, 'delete': False},
#         'ibug_detail':{'patch': True, 'get': True, 'delete': True},
#         'ibug_list':{'post': True,  'get': True},
#         'imodule_detail':{'patch': True, 'get': True, 'delete': True},
#         'imodule_list':{'post': True,  'get': True},
#         'ipriority_detail':{'patch': True, 'get': True, 'delete': True},
#         'ipriority_list':{'post': True,  'get': True},
#         'ireproducibility_detail':{'patch': True, 'get': True, 'delete': True},
#         'ireproducibility_list':{'post': True,  'get': True},
#         'irequirement_list':{'post': True, 'get': True},
#         'irequirements_detail':{'patch': True, 'get': True, 'delete': True},
#         'iseverity_detail':{'patch': True, 'get': True, 'delete': True},
#         'iseverity_list':{'post': True,  'get': True},
#         'isource_detail':{'patch': True, 'get': True, 'delete': True},
#         'isource_list':{'post': True,  'get': True},
#         'istatus_detail':{'patch': True, 'get': True, 'delete': True},
#         'istatus_list':{'post': True,  'get': True},
#         'itag_detail':{'patch': True, 'get': True, 'delete': True},
#         'itag_list':{'post': True,  'get': True},
#         'itask_detail':{'patch': True, 'get': True, 'delete': True},
#         'itask_list':{'post': True, 'get': True}
#     },

#     'Operator':{
#         'baseline_list': {'post': False,  'get': True},
#         'baseline_detail': {'patch': False, 'get': True, 'delete': True},
#         'package_list': {'post': True,  'get': True},
#         'package_detail': {'patch': True, 'get': True, 'delete': True},
#         'package_detail': {'patch': True, 'get': True, 'delete': False},
#         'package_merge': {'patch': False, 'get': True, 'delete': False},
#         'package_deploy':  {'patch': False, 'get': True, 'delete': False},
#         'project_list': {'post': False,  'get': True},
#         'project_detail': {'patch': False, 'get': True, 'delete': False},
#         'user_list': {'post': False,  'get': True},
#         'user_detail': {'patch': True, 'get': True, 'delete': False},
#         'subsystem_list': {'post': True,  'get': True},
#         'subsystem_detail': {'patch': True, 'get': True, 'delete': True},
#         'schema_list': {'post': True,  'get': True},
#         'schema_detail': {'patch': True, 'get': True, 'delete': True},
#         'agreement_list': {'post': True,  'get': True},
#         'agreement_detail': {'patch': True, 'get': True, 'delete': True},
#         'app_list': {'post': True,  'get': True},
#         'app_detail': {'patch': True, 'get': True, 'delete': True},
#         'blstatus_list': {'post': False,  'get': True},
#         'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
#         'machine_list': {'post': True,  'get': True},
#         'machine_detail': {'patch': True, 'get': True, 'delete': True},
#         'role_list': {'post': False,  'get': True},
#         'role_detail': {'patch': False, 'get': True, 'delete': False},
#         'database_list': {'post': True,  'get': True},
#         'database_detail': {'patch': True, 'get': True, 'delete': True},
#         'env_list': {'post': True,  'get': True},
#         'env_detail': {'patch': True, 'get': True, 'delete': True},
#         'credence_list': {'post': True,  'get': True},
#         'credence_detail': {'patch': True, 'get': True, 'delete': True},
#         'ibug_detail':{'patch': False, 'get': True, 'delete':False},
#         'ibug_list':{'post': False,  'get': True},
#         'imodule_detail':{'patch': True, 'get': True, 'delete': True},
#         'imodule_list':{'post': True,  'get': True},
#         'ipriority_detail':{'patch': True, 'get': True, 'delete': True},
#         'ipriority_list':{'post': True,  'get': True},
#         'ireproducibility_detail':{'patch':True, 'get': True, 'delete': True},
#         'ireproducibility_list':{'post':True,  'get': True},
#         'irequirement_list':{'post': False,  'get': True},
#         'irequirements_detail':{'patch': False, 'get': True, 'delete': False},
#         'iseverity_detail':{'patch': True, 'get': True, 'delete':True},
#         'iseverity_list':{'post':True,  'get': True},
#         'isource_detail':{'patch': True, 'get': True, 'delete': True},
#         'isource_list':{'post': True,  'get': True},
#         'istatus_detail':{'patch': True, 'get': True, 'delete': True},
#         'istatus_list':{'post': True,  'get': True},
#         'itag_detail':{'patch':True, 'get': True, 'delete': True},
#         'itag_list':{'post': True,  'get': True},
#         'itask_detail':{'patch': False, 'get': True, 'delete': True},
#         'itask_list':{'post': False, 'get': True},
#     },
#     'Anonymous':{
#         'baseline_list': {'post': False,  'get': False},
#         'baseline_detail': {'patch': False, 'get': False, 'delete': False},
#         'package_list': {'post': False,  'get': False},
#         'package_detail': {'patch': False, 'get': False, 'delete': False},
#         'package_merge': {'patch': False, 'get': False, 'delete': False},
#         'package_deploy':  {'patch': False, 'get': False, 'delete': False},
#         'package_release':  {'patch': False, 'get': False, 'delete': False},
#         'project_list': {'post': False,  'get': False},
#         'project_detail': {'patch': False, 'get': False, 'delete': False},
#         'user_list': {'post': True,  'get': False},
#         'user_detail': {'patch': False, 'get': False, 'delete': False},
#         'subsystem_list': {'post': False,  'get': False},
#         'subsystem_detail': {'patch': False, 'get': False, 'delete': False},
#         'schema_list': {'post': False,  'get': False},
#         'schema_detail': {'patch': False, 'get': False, 'delete': False},
#         'agreement_list': {'post': False,  'get': False},
#         'agreement_detail': {'patch': False, 'get': False, 'delete': False},
#         'app_list': {'post': False,  'get': False},
#         'app_detail': {'patch': False, 'get': False, 'delete': False},
#         'blstatus_list': {'post': False,  'get': False},
#         'blstatus_detail': {'patch': False, 'get': False, 'delete': False},
#         'machine_list': {'post': False,  'get': False},
#         'machine_detail': {'patch': False, 'get': False, 'delete': False},
#         'role_list': {'post': False,  'get': False},
#         'role_detail': {'patch': False, 'get': False, 'delete': False},
#         'database_list': {'post': False,  'get': False},
#         'database_detail': {'patch': False, 'get': False, 'delete': False},
#         'env_list': {'post': False,  'get': False},
#         'env_detail': {'patch': False, 'get': False, 'delete': False},
#         'credence_list': {'post': False,  'get': False},
#         'credence_detail': {'patch': False, 'get': False, 'delete': False},
#         'ibug_detail':{'patch': False, 'get': False, 'delete': False},
#         'ibug_list':{'post': False,  'get': False},
#         'imodule_detail':{'patch': False, 'get': False, 'delete': False},
#         'imodule_list':{'post': False,  'get': False},
#         'ipriority_detail':{'patch': False, 'get': False, 'delete': False},
#         'ipriority_list':{'post': False,  'get': False},
#         'ireproducibility_detail':{'patch': False, 'get': False, 'delete': False},
#         'ireproducibility_list':{'post': False,  'get': False},
#         'irequirement_list':{'post': False,  'get': False},
#         'irequirements_detail':{'patch': False, 'get': False, 'delete': False},
#         'iseverity_detail':{'patch': False, 'get': False, 'delete': False},
#         'iseverity_list':{'post': False,  'get': False},
#         'isource_detail':{'patch': False, 'get': False, 'delete': False},
#         'isource_list':{'post': False,  'get': False},
#         'istatus_detail':{'patch': False, 'get': False, 'delete': False},
#         'istatus_list':{'post': False,  'get': False},
#         'itag_detail':{'patch': False, 'get': False, 'delete': False},
#         'itag_list':{'post': False,  'get': False},
#         'itask_detail':{'patch': False, 'get': False, 'delete': False},
#         'itask_list':{'post': False, 'get': False}
#     },
# }


