#!/usr/bin/python
#-*- coding: UTF-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
import os


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template,attachments=None, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject,
                  recipients=to)
    #msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template, **kwargs)
    #处理附件
    if attachments is not None:
        for f in attachments:
            with app.open_resource(f) as fp:
                msg.attach(filename=os.path.basename(f), data=fp.read(),
                         content_type = 'application/octet-stream')
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
