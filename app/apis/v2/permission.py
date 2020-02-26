from flask import request, g


from flask_rest_jsonapi.exceptions import AccessDenied, JsonApiException


Permission={
    'Administrator':{
        'baseline_list': {'post': True,  'get': True},
        'baseline_detail': {'patch': True, 'get': True, 'delete': True},
        'package_list': {'post': True,  'get': True},
        'package_detail': {'patch': True, 'get': True, 'delete': True},
        'project_list': {'post': True,'get': True},
        'project_detail': {'patch': True, 'get': True, 'delete': True},
        'user_list': {'post': True,  'get': True},
        'user_detail': {'patch': True, 'get': True, 'delete': True},
        'subsystem_list ': {'post': True,  'get': True},
        'subsystem_detail': {'patch': True, 'get': True, 'delete': True},
        'schema_list': {'post': True,  'get': True},
        'schema_detail': {'patch': True, 'get': True, 'delete': True},
        'agreement_list': {'post': True,  'get': True},
        'agreement_detail': {'patch': True, 'get': True, 'delete': True},
        'app_list': {'post': True,  'get': True},
        'app_detail': {'patch': True, 'get': True, 'delete': True},
        'blstatus_list': {'post': True,  'get': True},
        'blstatus_detail': {'patch': True, 'get': True, 'delete': True},
        'machine_list': {'post': True,  'get': True},
        'machine_detail': {'patch': True, 'get': True, 'delete': True},
        'role_list': {'post': True,  'get': True},
        'role_detail': {'patch': True, 'get': True, 'delete': True},
        'database_list': {'post': True,  'get': True},
        'database_detail': {'patch': True, 'get': True, 'delete': True},
        'env_list': {'post': True,  'get': True},
        'env_detail': {'patch': True, 'get': True, 'delete': True},
        'credence_list': {'post': True,  'get': True},
        'credence_detail': {'patch': True, 'get': True, 'delete': True}
    }, 
    'Developer':{
        'baseline_list': {'post': True,  'get': True},
        'baseline_detail': {'patch': True, 'get': True, 'delete': False},
        'package_list': {'post': False,  'get': True},
        'package_detail': {'patch': False, 'get': True, 'delete': False},
        'project_list': {'post': False,  'get': True},
        'project_detail': {'patch': False, 'get': True, 'delete': False},
        'user_list': {'post': False,  'get': True},
        'user_detail': {'patch': True, 'get': True, 'delete': False},
        'subsystem_list': {'post': False,  'get': True},
        'subsystem_detail': {'patch': False, 'get': True, 'delete': False},
        'schema_list': {'post': False,  'get': False},
        'schema_detail': {'patch': False, 'get': False, 'delete': False},
        'agreement_list': {'post': False,  'get': False},
        'agreement_detail': {'patch': False, 'get': False, 'delete': False},
        'app_list': {'post': False,  'get': True},
        'app_detail': {'patch': False, 'get': True, 'delete': False},
        'blstatus_list': {'post': False,  'get': True},
        'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
        'machine_list': {'post': False,  'get': True},
        'machine_detail': {'patch': False, 'get': True, 'delete': False},
        'role_list': {'post': False,  'get': True},
        'role_detail': {'patch': False, 'get': True, 'delete': False},
        'database_list': {'post': False,  'get': True},
        'database_detail': {'patch': False, 'get': True, 'delete': False},
        'env_list': {'post': False,  'get': True},
        'env_detail': {'patch': False, 'get': True, 'delete': False},
        'credence_list': {'post': False,  'get': False},
        'credence_detail': {'patch': False, 'get': False, 'delete': False}
    },
    'Tester':{
        'baseline_list': {'post': False,  'get': True},
        'baseline_detail': {'patch': False, 'get': True, 'delete': False},
        'package_list': {'post': False,  'get': True},
        'package_detail': {'patch': False, 'get': True, 'delete': False},
        'project_list': {'post': False,  'get': True},
        'project_detail': {'patch': False, 'get': True, 'delete': False},
        'user_list': {'post': False,  'get': True},
        'user_detail': {'patch': True, 'get': True, 'delete': False},
        'subsystem_list': {'post': False,  'get': True},
        'subsystem_detail': {'patch': False, 'get': True, 'delete': False},
        'schema_list': {'post': False,  'get': False},
        'schema_detail': {'patch': False, 'get': False, 'delete': False},
        'agreement_list': {'post': False,  'get': False},
        'agreement_detail': {'patch': False, 'get': False, 'delete': False},
        'app_list': {'post': False,  'get': True},
        'app_detail': {'patch': False, 'get': True, 'delete': False},
        'blstatus_list': {'post': False,  'get': True},
        'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
        'machine_list': {'post': False,  'get': True},
        'machine_detail': {'patch': False, 'get': True, 'delete': False},
        'role_list': {'post': False,  'get': True},
        'role_detail': {'patch': False, 'get': True, 'delete': False},
        'database_list': {'post': False,  'get': True},
        'database_detail': {'patch': False, 'get': True, 'delete': False},
        'env_list': {'post': False,  'get': True},
        'env_detail': {'patch': False, 'get': True, 'delete': False},
        'credence_list': {'post': False,  'get': False},
        'credence_detail': {'patch': False, 'get': False, 'delete': False}
    },
    'Moderator':{
        'baseline_list': {'post': True,  'get': True},
        'baseline_detail': {'patch': True, 'get': True, 'delete': False},
        'package_list': {'post': True,  'get': True},
        'package_detail': {'patch': True, 'get': True, 'delete': False},
        'project_list': {'post': False,  'get': True},
        'project_detail': {'patch': False, 'get': True, 'delete': False},
        'user_list': {'post': False,  'get': True},
        'user_detail': {'patch': True, 'get': True, 'delete': False},
        'subsystem_list': {'post': False,  'get': True},
        'subsystem_detail': {'patch': False, 'get': True, 'delete': False},
        'schema_list': {'post': False,  'get': False},
        'schema_detail': {'patch': False, 'get': False, 'delete': False},
        'agreement_list': {'post': False,  'get': False},
        'agreement_detail': {'patch': False, 'get': False, 'delete': False},
        'app_list': {'post': False,  'get': True},
        'app_detail': {'patch': False, 'get': True, 'delete': False},
        'blstatus_list': {'post': False,  'get': True},
        'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
        'machine_list': {'post': False,  'get': True},
        'machine_detail': {'patch': False, 'get': True, 'delete': False},
        'role_list': {'post': False,  'get': True},
        'role_detail': {'patch': False, 'get': True, 'delete': False},
        'database_list': {'post': False,  'get': True},
        'database_detail': {'patch': False, 'get': True, 'delete': False},
        'env_list': {'post': False,  'get': True},
        'env_detail': {'patch': False, 'get': True, 'delete': False},
        'credence_list': {'post': False,  'get': False},
        'credence_detail': {'patch': False, 'get': False, 'delete': False}
    },
    'Operator':{
        'baseline_list': {'post': False,  'get': True},
        'baseline_detail': {'patch': False, 'get': True, 'delete': True},
        'package_list': {'post': True,  'get': True},
        'package_detail': {'patch': True, 'get': True, 'delete': True},
        'project_list': {'post': False,  'get': True},
        'project_detail': {'patch': False, 'get': True, 'delete': False},
        'user_list': {'post': False,  'get': True},
        'user_detail': {'patch': True, 'get': True, 'delete': False},
        'subsystem_list': {'post': True,  'get': True},
        'subsystem_detail': {'patch': True, 'get': True, 'delete': True},
        'schema_list': {'post': True,  'get': True},
        'schema_detail': {'patch': True, 'get': True, 'delete': True},
        'agreement_list': {'post': True,  'get': True},
        'agreement_detail': {'patch': True, 'get': True, 'delete': True},
        'app_list': {'post': True,  'get': True},
        'app_detail': {'patch': True, 'get': True, 'delete': True},
        'blstatus_list': {'post': False,  'get': True},
        'blstatus_detail': {'patch': False, 'get': True, 'delete': False},
        'machine_list': {'post': True,  'get': True},
        'machine_detail': {'patch': True, 'get': True, 'delete': True},
        'role_list': {'post': False,  'get': True},
        'role_detail': {'patch': False, 'get': True, 'delete': False},
        'database_list': {'post': True,  'get': True},
        'database_detail': {'patch': True, 'get': True, 'delete': True},
        'env_list': {'post': True,  'get': True},
        'env_detail': {'patch': True, 'get': True, 'delete': True},
        'credence_list': {'post': True,  'get': True},
        'credence_detail': {'patch': True, 'get': True, 'delete': True}
    },
    'Anonymous':{
        'baseline_list': {'post': False,  'get': False},
        'baseline_detail': {'patch': False, 'get': False, 'delete': False},
        'package_list': {'post': False,  'get': False},
        'package_detail': {'patch': False, 'get': False, 'delete': False},
        'project_list': {'post': False,  'get': False},
        'project_detail': {'patch': False, 'get': False, 'delete': False},
        'user_list': {'post': True,  'get': False},
        'user_detail': {'patch': False, 'get': False, 'delete': False},
        'subsystem_list': {'post': False,  'get': False},
        'subsystem_detail': {'patch': False, 'get': False, 'delete': False},
        'schema_list': {'post': False,  'get': False},
        'schema_detail': {'patch': False, 'get': False, 'delete': False},
        'agreement_list': {'post': False,  'get': False},
        'agreement_detail': {'patch': False, 'get': False, 'delete': False},
        'app_list': {'post': False,  'get': False},
        'app_detail': {'patch': False, 'get': False, 'delete': False},
        'blstatus_list': {'post': False,  'get': False},
        'blstatus_detail': {'patch': False, 'get': False, 'delete': False},
        'machine_list': {'post': False,  'get': False},
        'machine_detail': {'patch': False, 'get': False, 'delete': False},
        'role_list': {'post': False,  'get': False},
        'role_detail': {'patch': False, 'get': False, 'delete': False},
        'database_list': {'post': False,  'get': False},
        'database_detail': {'patch': False, 'get': False, 'delete': False},
        'env_list': {'post': False,  'get': False},
        'env_detail': {'patch': False, 'get': False, 'delete': False},
        'credence_list': {'post': False,  'get': False},
        'credence_detail': {'patch': False, 'get': False, 'delete': False}
    }
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
    print(role,request.endpoint)
    print(Permission.get('Administrator').get('app_list'))
    if Permission.get(role,'Anonymous').get(request.endpoint).get(view.__name__) == False :
        raise AccessDenied(detail='Access Denied')