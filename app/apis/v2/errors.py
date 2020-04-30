# -*- coding: utf-8 -*-

from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def api_abort(status, detail=None, **kwargs):
    if detail is None:
        detail = HTTP_STATUS_CODES.get(status, '')

    response = jsonify(errors=[{
        'status': status,
        'detail': detail
    }],
                       jsonapi={"version": "1.0"},
                       **kwargs)
    response.status_code = status
    return response  # You can also just return (response, code) tuple


def invalid_token():
    response = api_abort(
        401,
        error='invalid_token',
        error_description='Either the token was expired or invalid.')
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


def token_missing():
    response = api_abort(401)
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


def access_denied():
    """Throw this error when requested resource owner doesn't match the user of the ticket"""
    response = api_abort(
        403,
        error='Access denied',
        error_description='Either the token was expired or invalid.')
    return response


class ValidationError(ValueError):
    pass


# from app.apis.v2 import api_v2
# @api_v2.errorhandler(ValidationError)
# def validation_error(e):
#     return api_abort(400, e.args[0])
