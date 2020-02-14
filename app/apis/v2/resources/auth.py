# -*- coding: utf-8 -*-

from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired


from  app import flask_app
from app.models.auth import Project, User, group, Role
from app import db

from app.apis.v2 import api
from app.apis.v2.schemas.auth import ProjectSchema, UserSchema, RoleSchema

from flask import jsonify, request, current_app, url_for, g
from flask.views import MethodView

from app.apis.v2 import api_v2
from app.apis.v2.auth import auth_required, generate_token, get_token
from app.apis.v2.errors import api_abort, ValidationError
from app.models.auth import User


class AuthTokenAPI(MethodView):
    
    def post(self):
        grant_type = request.json.get('grant_type')
        email = request.json.get('email')
        password = request.json.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(code=400, message='The grant type must be password.')

        user = User.query.filter_by(email=email).first()
        if user is None or not user.verify_password(password):
            return api_abort(code=400, message='Either the email or password was invalid.')

        token, expiration = generate_token(user)

        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response

# 根据token返回用户信息
@api_v2.route('/tokeninfo')
def token_user():
    token_type, token = get_token()
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False
    user = User.query.get(data['id'])   
    response = jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
        })
    return response




# Create resource managers
# 项目
class ProjectList(ResourceList):
    def after_create_object(self, obj, data, view_kwargs):
        print('*'*50)
        print(data)
        print(obj.name)
    schema = ProjectSchema
    data_layer = {'session': db.session,
                  'model': Project,
                  'methods': {'after_create_object': after_create_object}}


class ProjectDetail(ResourceDetail):
    schema = ProjectSchema
    data_layer = {'session': db.session,
                  'model': Project}

class ProjectRelationship(ResourceRelationship):
    schema = ProjectSchema
    data_layer = {'session': db.session,
                  'model': Project}

# 用户
class UserList(ResourceList):
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}

class UserDetail(ResourceDetail):
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}

class UserRelationship(ResourceRelationship):
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}

# 角色
class RoleList(ResourceList):
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}

class RoleDetail(ResourceDetail):
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}

class RoleRelationship(ResourceRelationship):
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}
        
# Create endpoints
#项目
api.route(ProjectList, 'project_list', '/api/projects')
api.route(ProjectDetail, 'project_detail', '/api/projects/<int:id>')
api.route(ProjectRelationship, 'project_users', '/api/projects/<int:id>/relationships/users')
#用户
api.route(UserList, 'user_list', '/api/users')
api.route(UserDetail, 'user_detail', '/api/users/<int:id>')
api.route(UserRelationship, 'user_projects', '/api/users/<int:id>/relationships/projects')
api.route(UserRelationship, 'user_role', '/api/users/<int:id>/relationships/role')
#角色
api.route(RoleList, 'role_list', '/api/roles')
api.route(RoleDetail, 'role_detail', '/api/roles/<int:id>')
api.route(RoleRelationship, 'role_users', '/api/roles/<int:id>/relationships/users')

#生成token端点
api_v2.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])