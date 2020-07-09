from flask import request, jsonify

from app.apis.v2 import api_v2
from app.apis.v2.message import api_abort
from app.utils.execute_cmd import remote_execute_command


@api_v2.route('/account/svn/user/create', methods=['POST'])
def svn_user_create():
    json_data = request.get_json()
    username = json_data['data']['attributes']['username']
    password = json_data['data']['attributes']['password']
    command = f'sudo htpasswd -b /u01/svndata/svnpasswd/passwd {username} {password}'
    try:
        remote_execute_command('192.168.0.43',
                               command,
                               port=22,
                               username='redhat',
                               password='s0Icjgp,bk5Vzx')
    except Exception as e:
        return api_abort(400, '创建SVN用户失败'+str(e))
    else:
        return jsonify(data=[{'status': 200, 'detail': '创建SVN用户成功'}])

@api_v2.route('/account/svn/user/password/reset', methods=['POST'])
def svn_user_password_reset():
    json_data = request.get_json()
    username = json_data['data']['attributes']['username']
    password = json_data['data']['attributes']['password']
    command = f'sudo htpasswd -b /u01/svndata/svnpasswd/passwd {username} {password}'
    try:
        remote_execute_command('192.168.0.43',
                               command,
                               port=22,
                               username='redhat',
                               password='s0Icjgp,bk5Vzx')
    except Exception as e:
        return api_abort(400, 'SVN密码重置成功失败'+str(e))
    else:
        return jsonify(data=[{'status': 200, 'detail': 'SVN密码重置成功'}])