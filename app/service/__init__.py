#!/usr/bin/python
#-*- coding: UTF-8 -*-
from flask import Blueprint

service_bp = Blueprint('service', __name__)

from . import views