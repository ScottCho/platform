#!/usr/bin/python
#-*- coding: UTF-8 -*-
from flask import Blueprint

log_bp = Blueprint('log', __name__)

from . import views