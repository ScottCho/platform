#-*- coding: UTF-8 -*-
from flask_rest_jsonapi import Api

from app import  flask_app

api = Api(flask_app)

from app.apis.resources import auth, cmdb, service