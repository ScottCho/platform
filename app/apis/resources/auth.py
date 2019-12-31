from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship

from  app import flask_app
from app.models.auth import Project
from app import db

from app.apis import api

class ProjectSchema(Schema):
    class Meta:
        type_ = 'project'
        self_view = 'project_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'project_list'

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    zh_name = fields.Str(required=True)

class ProjectMany(ResourceList):
    schema = ProjectSchema
    data_layer = {'session': db.session,
                  'model': Project}

class ProjectOne(ResourceDetail):
    schema = ProjectSchema
    data_layer = {'session': db.session,
                  'model': Project}

api.route(ProjectMany, 'project_list', '/api/projects')
api.route(ProjectOne, 'project_detail', '/api/projects/<int:id>')