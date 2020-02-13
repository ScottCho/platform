# -*- coding: utf-8 -*-

from flask import jsonify, request, current_app, url_for, g
from flask.views import MethodView

from app.apis.v1 import api_v1


class IndexAPI(MethodView):

    def get(self):
        return jsonify({
            "api_version": "1.0",
            "api_base_url": "http://127.0.0.1/api/v1",
            "current_user_url": "http://127.0.0.1/api/v1/user",
            "authentication_url": "http://127.0.0.1/api/v1/token",
            "user_url": "http://127.0.0.1/api/v1/users/{user_id }",
            "current_user_items_url": "http://127.0.0.1/api/v1/user/items{?page,per_page}",
            "current_user_active_items_url": "http://127.0.0.1/api/v1/user/items/active{?page,per_page}",
            "current_user_completed_items_url": "http://127.0.0.1/api/v1/user/items/completed{?page,per_page}",
        })

api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])

