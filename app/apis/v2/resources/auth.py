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
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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
from flask_rest_jsonapi.exceptions import AccessDenied, JsonApiException

# 返回登录产生的token
class AuthTokenAPI(MethodView):
    def post(self):
        grant_type = request.json.get('grant_type')
        email = request.json.get('email')
        password = request.json.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(400, 'The grant type must be password.')

        user = User.query.filter_by(email=email).first()
        if user is None or not user.verify_password(password):
            return api_abort(400, 'Either the email or password was invalid.')

        token, expiration = generate_token(user)

        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response

# 注册用户
class RegisterAPI(MethodView):
    def post(self):
        email = request.json.get('email')
        password = request.json.get('password')
        role_id = request.json.get('role_id',1)
        username = request.json.get('username')
        if User.query.filter_by(email=email).first():
            return api_abort(409,'email已经被注册')
        if User.query.filter_by(username=username).first():
            return api_abort(409,'用户名已经被注册')
        user = User(email=email,
                    username=username,
                    password=password,
                    role_id=role_id
                    )
        db.session.add(user)
        db.session.commit() 
        token = user.generate_confirmation_token()
        print('开始发送邮件')
        send_email([user.email],'确认您的账户',
            'apis/v2/confirm.html',user=user,token=token)
        return api_abort(200,'请在邮箱中的链接确认用户')


# 无需登录确认用户
# class ConfirmUserAPI(MethodView):
#     def get(self,token):
#         s = Serializer(current_app.config['SECRET_KEY'])
#         try:
#             data = s.loads(token.encode('utf-8'))
#             user_id = data.get('confirm')
#             user = User.query.get(user_id)
#             user.confirmed = True
#             db.session.add(user)
#             db.session.commit()
#         except:
#             return api_abort(400,'链接无效或者过期')
#         return jsonify(data=[{'status':201, 'detail':'账户已激活'}], jsonapi={"version": "1.0"})
            

# 确认用户
class ConfirmUserAPI(MethodView):
    def get(self,token):
        if g.current_user.confirm(token) or g.current_user.confirmed:
            db.session.commit()
        else:
            return api_abort(400,'链接无效或者过期')
        return jsonify(data=[{'status':201, 'detail':'账户已激活'}], jsonapi={"version": "1.0"})


# 重置密码请求
class PasswordResetRequestAPI(MethodView):
    def post(self):
        email = request.json.get('data').get('attributes').get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_reset_token()
            send_email([email], 'Frog平台-重置密码',
                       'mail/api/auth/reset_password.html',
                       user=user, token=token)
            return jsonify(data=[{'status':201, 'detail':'请查收重置密码邮件'}])
        else:
            return api_abort(400,'邮箱不存在')

# 重置密码
class PasswordResetAPI(MethodView):
    # def get(self,token):
    #     return redirect

    def post(self,token):
        password = request.json.get('data').get('attributes').get('password')
        if User.reset_password(token, password):
            db.session.commit()
            return jsonify(data=[{'status':201, 'detail':'密码重置成功'}])
        else:
            return api_abort(400,'密码重置失败')
# 修改密码
class PasswordChangeAPI(MethodView):
    decorators = [auth_required]
    def post(self):
        old_password = request.json.get('data').get('attributes').get('old_password')
        print(old_password)
        new_password = request.json.get('data').get('attributes').get('new_password')
        if g.current_user.verify_password(old_password):
            g.current_user.password = new_password
            db.session.add(g.current_user)
            db.session.commit()
            return jsonify(data=[{'status':201, 'detail':'密码更新成功'}])
        else:
            return api_abort(400,'密码更新失败')

# 根据token返回用户信息
@api_v2.route('/tokeninfo')
def token_user():
    token_type, token = get_token()
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return api_abort(status=400, detail='The token expired or invalid.')
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
            'apis/v2/confirm.html',user=obj,token=token)
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
api.route(ProjectRelationship, 'project_apps', '/api/projects/<int:id>/relationships/apps')
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
# 注册用户
api_v2.add_url_rule('/register/user', view_func=RegisterAPI.as_view('register_user'), methods=['POST'])
# 确认用户端点
api_v2.add_url_rule('/confirm/user/<token>', view_func=ConfirmUserAPI.as_view('confirm_user'), methods=['GET',])
#　重置密码请求
api_v2.add_url_rule('/password/reset', view_func=PasswordResetRequestAPI.as_view('password_reset_request'), methods=['POST',])
api_v2.add_url_rule('/password/reset/<token>', view_func=PasswordResetAPI.as_view('password_reset'), methods=['POST',])
# 更新密码
api_v2.add_url_rule('/password/change', view_func=PasswordChangeAPI.as_view('password_change'), methods=['POST',])
