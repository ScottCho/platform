# -*- coding: utf-8 -*-

from flask import url_for

from app.models.auth import User


def user_schema(user):
    return {
        'id': user.id,
        'self': url_for('.user', user_id=user.id, _external=True),
        'kind': 'User',
        'username': user.username,
    }


def users_schema(users, current, prev, next, pagination):
    return {
        'self': current,
        'kind': 'ItemCollection',
        'items': [user_schema(user) for user in users],
        'prev': prev,
        'last': url_for('.users', page=pagination.pages, _external=True),
        'first': url_for('.users', page=1, _external=True),
        'next': next,
        'count': pagination.total
    }
