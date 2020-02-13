from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship

from  app import flask_app
from app.models.auth import Project, User, group, Role
from app import db

from app.apis.v2 import api

# Create logical data abstraction
# 项目
class ProjectSchema(Schema):
    class Meta:
        type_ = 'project'
        self_view = 'project_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'project_list'
        
    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    zh_name = fields.Str(required=True)
    source_dir = fields.Str()
    target_dir = fields.Str()
    switch = fields.Bool()
    users = Relationship(self_view='project_users',
                             self_view_kwargs={'id': '<id>'},
                             related_view='user_list',
                             related_view_kwargs={'id': '<id>'},
                             many=True,
                             schema='UserSchema',
                             type_='user')

# 用户
class UserSchema(Schema):
    class Meta:
        type_ = 'user'
        self_view = 'user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'user_list'

    id = fields.Integer(as_string=True, dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    created = fields.Str()
    last_seen = fields.Str()
    confirmed = fields.Bool()
    active = fields.Bool()
    projects = Relationship(self_view='user_projects',
                           self_view_kwargs={'id': '<id>'},
                           related_view='project_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='ProjectSchema',
                           type_='project')                     
    role = Relationship(self_view='user_role',
                        self_view_kwargs={'id': '<id>'},
                        related_view='role_detail',
                        related_view_kwargs={'id': '<role_id>'},
                        schema='RoleSchema',
                        type_='role')

# 角色
class RoleSchema(Schema):
    class Meta:
        type_ = 'Role'
        self_view = 'role_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'role_list'

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    permissions = fields.Integer(required=True,  load_only=True)
    users = Relationship(self_view='role_users',
                        self_view_kwargs={'id': '<id>'},
                        related_view='user_list',
                        related_view_kwargs={'id': '<id>'},
                        many=True,
                        schema='UserSchema', 
                        type_ = 'user'     
    )


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