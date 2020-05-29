from collections import ChainMap

from flask import request, g


from flask_rest_jsonapi.exceptions import AccessDenied, JsonApiException

# 默认权限
default = {
        'baseline_list': {'post': False,  'get': True},
        'baseline_detail': {'patch': False, 'get': True, 'delete': False},
        'package_list': {'post': False,  'get': True},
        'package_detail': {'patch': False, 'get': True, 'delete': False},
        'package_merge': {'patch': False, 'get': False, 'delete': False},
        'package_deploy': {'patch': False, 'get': False, 'delete': False},
        'package_release': {'patch': False, 'get': False, 'delete': False},
        'package_download': {'GET': True},
        'project_list': {'post': False, 'get': True},
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
        'server_list': {'post': False,  'get': False},
        'server_detail': {'patch': False, 'get': False, 'delete': False},
        'role_list': {'post': False,  'get': True},
        'role_detail': {'patch': False, 'get': False, 'delete': False},
        'database_list': {'post': False,  'get': False},
        'database_detail': {'patch': False, 'get': False, 'delete': False},
        'env_list': {'post': False,  'get': True},
        'env_detail': {'patch': False, 'get': False, 'delete': False},
        'credence_list': {'post': False,  'get': False},
        'credence_detail': {'patch': False, 'get': False, 'delete': False},
        'issue_bug_detail': {'patch':False, 'get': True, 'delete': False},
        'issue_bug_list':{'post': False,  'get': True},
        'issue_module_detail': {'patch': False, 'get': True, 'delete': False},
        'issue_module_list': {'post': False,  'get': True},
        'issue_priority_detail': {'patch': False, 'get': True, 'delete': False},
        'issue_priority_list': {'post': False,  'get': True},
        'issue_reproducibility_detail':{'patch': False, 'get': True, 'delete': False},
        'issue_reproducibility_list':{'post': False,  'get': True},
        'issue_requirement_list': {'post': False,  'get': True},
        'issue_requirement_detail': {'patch': False, 'get': True, 'delete': False},
        'issue_severity_detail': {'patch': False, 'get': True, 'delete': False},
        'issue_severity_list': {'post': False,  'get': True},
        'issue_source_detail': {'patch': False, 'get': True, 'delete': False},
        'issue_source_list': {'post': False,  'get': True},
        'issue_upload': {'post': False},
        'status_detail':{'patch': False, 'get': True, 'delete': False},
        'status_list': {'post': False,  'get': True},
        'tag_detail': {'patch': False, 'get': True, 'delete': False},
        'tag_list': {'post': False,  'get': True},
        'issue_task_detail': {'patch': False, 'get': True, 'delete': False},
        'issue_task_list': {'post': False, 'get': True},
        'api_v2.confirm_user': {'get': True},
        'api_v2.password_change': {'post': True},
        'api_v2.password_reset': {'post': True, 'get': True},
        'api_v2.password_reset_request': {'get': True},
        'api_v2.register_user': {'post': True},
        'api_v2.token': {'post': True},
        'api_v2.token_user': {'get': True},
        'api_v2.app_manage': {'get': False},
        'api_v2.database_manage': {'get': False},
        'api_v2.stat': {'get': True},
        'bgtask_detail': {'patch': False, 'get': False, 'delete': False},
        'bgtask_list': {'post': False, 'get': False},
        'link_detail': {'get': True},
        'link_list': {'get': True},
        'software_detail': {'patch': False, 'get': False, 'delete': False},
        'software_list': {'post': False, 'get': False},
}

# 发布与更新基线
baseline_update = {
    'baseline_list': {'post': True,  'get': True},
    'baseline_detail': {'patch': True, 'get': True, 'delete': False}
}

# 基线管理
baseline_management = {
    'baseline_list': {'post': True,  'get': True},
    'baseline_detail': {'patch': True, 'get': True, 'delete': True}
}

# 更新包发布
package_management = {
        'package_list': {'post': True,  'get': True},
        'package_detail': {'get': True, 'delete':False},
        'package_merge': {'get': True},
        'package_deploy': {'get': True},
        'package_release': {'get': True}
}

# 项目管理
project_management = {
    'project_list': {'post': True,'get': True},
    'project_detail': {'patch': True, 'get': True, 'delete': True}
}

# 用户管理
user_management = {
    'user_list': {'post': True,  'get': True},
    'user_detail': {'patch': True, 'get': True, 'delete': True}
}

# 角色管理
role_management = {
    'role_list': {'post': True,  'get': True},
    'role_detail': {'patch': True, 'get': True, 'delete': True}
}

# CMDB
cmdb = {
    'subsystem_list': {'post': True,  'get': True},
    'subsystem_detail': {'patch': True, 'get': True, 'delete': True},
    'schema_list': {'post': True,  'get': True},
    'schema_detail': {'patch': True, 'get': True, 'delete': True},
    'agreement_list': {'post': True,  'get': True},
    'agreement_detail': {'patch': True, 'get': True, 'delete': True},
    'server_list': {'post': True,  'get': True},
    'server_detail': {'patch': True, 'get': True, 'delete': True},
    'env_list': {'post': True,  'get': True},
    'env_detail': {'patch': True, 'get': True, 'delete': True},
    'credence_list': {'post': True,  'get': True},
    'credence_detail': {'patch': True, 'get': True, 'delete': True},
    'status_detail': {'patch': True, 'get': True, 'delete': True}
}

# 服务管理
service_management = {
    'database_list': {'post': True,  'get': True},
    'database_detail': {'patch': True, 'get': True, 'delete': True},
    'app_list': {'post': True,  'get': True},
    'app_detail': {'patch': True, 'get': True, 'delete': True},
    'api_v2.app_manage': {'get': True},
    'api_v2.database_manage': {'get': True}
}

# 软件安装和管理
software_management = {
    'software_detail': {'patch': True, 'get': True, 'delete': True},
    'software_list': {'post': True, 'get': True},
    'bgtask_detail': {'patch': True, 'get': True, 'delete': True},
    'bgtask_list': {'post': True, 'get': True}
}

# bug和任务管理，测试可以提交和关闭
bug_task_management = {
    'issue_bug_detail': {'patch':True, 'get': True, 'delete': True},
    'issue_bug_list': {'post': True, 'get': True},
    'issue_task_detail': {'patch': True, 'get': True, 'delete': True},
    'issue_task_list': {'post': True, 'get': True}
}

# issue管理, 经理权限
issue_management = {
    'issue_requirement_list':{'post': True,  'get': True},
    'issue_requirement_detail':{'patch': True, 'get': True, 'delete': True},
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
    'status_detail':{'patch': True, 'get': True, 'delete': True},
    'tag_detail':{'patch': True, 'get': True, 'delete': True},
    'tag_list':{'post': True,  'get': True},
    'issue_upload': {'post': True},  
}

Permission = {

    # 管理员
    'Administrator': ChainMap(
                             baseline_management, package_management, \
                             project_management, user_management, \
                             role_management, cmdb, \
                             service_management, issue_management, \
                             software_management, default
                             ),

    # 开发
    'Developer': ChainMap(baseline_update, default),
    # 测试
    'Tester': ChainMap(bug_task_management, default),
    # 经理
    'Manager': ChainMap(issue_management, default),
    # 协管员
    'Moderator': ChainMap(
                            package_management, baseline_update, \
                            service_management, issue_management, default
                        ),
    # 运维
    'Operator': ChainMap(
                          cmdb, service_management, package_management, \
                          software_management, default),                    
    # 匿名用户
    'Anonymous': ChainMap(default)
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
    except Exception:
        raise JsonApiException(detail='Unauthorized.', status=401)

    # request.endpoint=project_list   view.__name__=get
    if Permission.get(role, 'Anonymous').get(request.endpoint).get(view.__name__) == False :
        raise AccessDenied(detail='Access Denied')
