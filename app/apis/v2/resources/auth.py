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
from app.localemail import send_email

# 返回登录产生的token
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

# 确认用户
class ConfirmUserAPI(MethodView):
    def get(self,token):
        if g.current_user.confirmed:
            response = jsonify({
                'code': 200,
                'message': g.current_user.username+'早已激活'
            })
        elif g.current_user.confirm(token):
            db.session.commit()
            response = jsonify({
                'code': 200,
                'message': g.current_user.username+'已激活'
            })
        else:
            return api_abort(400,'链接无效或者过期')
        return response

# 根据token返回用户信息
@api_v2.route('/tokeninfo')
def token_user():
    token_type, token = get_token()
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return api_abort(code=400, message='The token expired or invalid.')
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
    decorators = (auth_required,)
    schema = ProjectSchema
    data_layer = {'session': db.session,
                  'model': Project}


class ProjectDetail(ResourceDetail):
    decorators = (auth_required,)
    schema = ProjectSchema
    data_layer = {'session': db.session,
                  'model': Project}

class ProjectRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = ProjectSchema
    data_layer = {'session': db.session,
                  'model': Project}

# 用户
class UserList(ResourceList):
    decorators = (auth_required,)
    # 自定义post方法,注册用户
    def post(self, *args, **kwargs):
        """Create an object"""
        json_data = request.get_json() or {}

        qs = QSManager(request.args, self.schema)

        schema = compute_schema(self.schema,
                                getattr(self, 'post_schema_kwargs', dict()),
                                qs,
                                qs.include)

        try:
            data, errors = schema.load(json_data)
        except IncorrectTypeError as e:
            errors = e.messages
            for error in errors['errors']:
                error['status'] = '409'
                error['title'] = "Incorrect type"
            return errors, 409
        except ValidationError as e:
            errors = e.messages
            for message in errors['errors']:
                message['status'] = '422'
                message['title'] = "Validation error"
            return errors, 422

        if errors:
            for error in errors['errors']:
                error['status'] = "422"
                error['title'] = "Validation error"
            return errors, 422

        username = data['username']
        email = data['email']
        if User.query.filter_by(email=email).first():
            return api_abort(409,'email已经被注册')
        if User.query.filter_by(username=username).first():
            return api_abort(409,'用户名已经被注册')
        
        self.before_post(args, kwargs, data=data)

        obj = self.create_object(data, kwargs)
        token = obj.generate_confirmation_token()
        send_email([email],'确认您的账户',
            'mail/auth/confirm.html',user=obj,token=token)
        result = schema.dump(obj).data

        if result['data'].get('links', {}).get('self'):
            final_result = (result, 201, {'Location': result['data']['links']['self']})
        else:
            final_result = (result, 201)

        result = self.after_post(final_result)

        return result

    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}

class UserDetail(ResourceDetail):
    decorators = (auth_required,)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}

class UserRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}

# 角色
class RoleList(ResourceList):
    decorators = (auth_required,)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}

class RoleDetail(ResourceDetail):
    decorators = (auth_required,)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}

class RoleRelationship(ResourceRelationship):
    decorators = (auth_required,)
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
# 确认用户端点
api_v2.add_url_rule('/confirm/<token>', view_func=ConfirmUserAPI.as_view('confirm_user'), methods=['GET',])
