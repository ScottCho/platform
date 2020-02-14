#-*- coding: UTF-8 -*-
from flask import Blueprint
from flask_rest_jsonapi import Api

from app import  flask_app
from app.apis.v2.auth import auth_required


api_v2 = Blueprint('api_v2', __name__)
# from app.apis.v2 import resources
# api = Api(flask_app,decorators=(auth_required,))
# api.init_app(flask_app)
api = Api(flask_app)
from app.apis.v2.resources import auth, cmdb, service, vcs


