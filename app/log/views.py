from . import log_bp
from flask import render_template

import logging


@log_bp.route('/downloadlog')
def downloadlog():
	return  render_template('log/downloadlog.html')

@log_bp.route('/downloadapp')
def downloadapp():
	return  render_template('log/downloadapp.html')