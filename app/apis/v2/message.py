# -*- coding: utf-8 -*-

from flask import jsonify

status_msg = {
    200: '成功',
    10000: 'SVN操作异常',
    10011: '字符集解析错误',
    10012: '密码不合法',
    10013: '二次密码不一致',
    10014: '手机号不合法',
    10015: '邮箱不合法',
    10016: '请登录后使用',
    10017: 'token不可使用',
    10018: '修改用户错误',
    10019: '删除错误',
    10020: '修改的角色不存在',
    10021: '没有此权限可删除',
    10022: '没有此数据',
    10023: '没有上传文件',
    10024: '文件格式不符合规范',
    20000: '异常错误'
}


def success_msg(status=200, data=None, msg=None):
    response = jsonify({
        'status': status,
        'data': data,
        'msg': msg if msg else status_msg.get(status, '')
    })
    return response


def api_abort(status, detail=None, **kwargs):
    if detail is None:
        detail = status_msg.get(status, '')

    response = jsonify(errors=[{
        'status': status,
        'detail': detail
    }],
                       jsonapi={"version": "1.0"},
                       **kwargs)
    return response  # You can also just return (response, code) tuple


def invalid_token():
    response = api_abort(
        401,
        error='invalid_token',
        error_description='Either the token was expired or invalid.')
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


def token_missing():
    response = api_abort(401)
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


def access_denied():
    response = api_abort(
        403,
        error='Access denied',
        error_description='Either the token was expired or invalid.')
    return response
