#-*- coding: UTF-8 -*-
from flask import Blueprint

backstage_bp = Blueprint('backstage', __name__)

from . import views