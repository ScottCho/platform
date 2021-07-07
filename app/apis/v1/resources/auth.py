# -*- coding: utf-8 -*-

from flask import jsonify, request, current_app, url_for, g
from flask.views import MethodView

from app.apis.v1 import api_v1
from app.apis.v1.auth import auth_required, generate_token
from app.apis.v1.errors import api_abort, ValidationError
from app.apis.v1.schemas.auth import user_schema, users_schema
from app import db
from app.models.auth import User


class AuthTokenAPI(MethodView):
    
    def post(self):
        grant_type = request.form.get('grant_type')
        email = request.form.get('email')
        password = request.form.get('password')

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


class UserDetail(MethodView):
    decorators = [auth_required]

    def get(self, user_id):
        """Get user."""
        user = User.query.get_or_404(user_id)
        return jsonify(user_schema(user))

    def patch(self, user_id):
        """Update item."""
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        username = data.get('username')
        print(username)
        if username is None or str(username).strip() == '':
            raise ValidationError('The user username was empty or invalid.')
        user.username = username
        db.session.commit()
        return '', 204

    def delete(self, user_id):
        """Delete user."""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

class UserList(MethodView):
    # decorators = [auth_required]

    def get(self):
        """Get current user's all users."""
        page = request.args.get('page', 1, type=int)
        per_page = 10
        pagination = User.query.order_by(User.id).paginate(page, per_page)
        users = pagination.items
        current = url_for('.users', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.users', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.users', page=page + 1, _external=True)
        return jsonify(users_schema(users, current, prev, next, pagination))

    def post(self):
        """Create new user."""
        data = request.get_json()
        user = User(email=data.get('email'),
                    username=data.get('username'),
                    password=data.get('password'),
                    role_id=data.get('role_id')
                    )
        db.session.add(user)
        db.session.commit()
        response = jsonify(user_schema(user))
        response.status_code = 201
        response.headers['Location'] = url_for('.user', item_id=user.id, _external=True)
        return response




api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])
api_v1.add_url_rule('/users/<int:user_id>', view_func=UserDetail.as_view('user'),
                    methods=['GET', 'PATCH', 'DELETE'])
api_v1.add_url_rule('/users/', view_func=UserList.as_view('users'),
                    methods=['GET','POST'])