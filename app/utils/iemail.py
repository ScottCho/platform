# -*- coding:UTF-8 -*-
# AUTHOR: Zhao Yong
# FILE: /Code/githup/platform/app/utils/iemail.py
# DATE: 2020/04/30 Thu

from __future__ import unicode_literals
import os
import smtplib
from email.header import Header as _Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr

from flask import render_template
from app import flask_app


MAIL_SERVER = os.getenv('MAIL_SERVER','smtp.exmail.qq.com')
# 25端口连接SMTP服务器是明文传输,这里选择加密SMTP会话， 更安全地发送邮件
SMTP_PORT = os.getenv('SMTP_PORT',465)
MAIL_USERNAME = os.getenv('MAIL_USERNAME','xxxx@xxxx')
MAIL_PASSWORD =  os.getenv('MAIL_PASSWORD','JwnbKvR6bshSLWrGddd')

TO_ADDRS = ['scottcho@qq.com']


def Header(name):  # noqa
    return _Header(name, 'utf-8').encode()


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name), addr))


# nick_from发件人昵称，默认为发件人邮箱
# nick_to收件人昵称
def gen_msg(to_addrs, content, subject, nick_to,nick_from=None, attachments=None):
    if nick_from is None:
        nick_from = 'Forg平台'
    msg = MIMEMultipart()
    msg['From'] = _format_addr('{} <{}>'.format(nick_from, MAIL_USERNAME))
    msg['To'] = _format_addr('{} <{}>'.format(nick_to, to_addrs))
    msg['Subject'] = Header(subject)
    msg.attach(MIMEText(content, 'html', 'gbk'))

    if attachments is not None:
        for attachment in attachments:
            attach = MIMEText(open(attachment, 'rb').read(), 'base64', 'utf-8')
            attach['Content-Type'] = 'application/octet-stream'
            attach['Content-Disposition'] = 'attachment; filename="{}"'.format(
                os.path.basename(attachment))
            msg.attach(attach)
    return msg


def send_email(to_addrs, content, subject, nick_to, attachments=None, nick_from=None):
    msg = gen_msg(to_addrs, content, subject, attachments, nick_from)
    server = smtplib.SMTP_SSL(MAIL_SERVER, SMTP_PORT)
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    server.sendmail(MAIL_USERNAME, TO_ADDRS, msg.as_string())
    server.quit()



rows_data = [
    [34, 72, 38, 30, 75, 48, 75],
    [6, 24, 1, 84, 54, 62, 60],
    [28, 79, 97, 13, 85, 93, 93],
    [27, 71, 40, 17, 18, 79, 90],
    [88, 25, 33, 23, 67, 1, 59],
    [24, 100, 20, 88, 29, 33, 38],
    [6, 57, 88, 28, 10, 26, 37],
    [52, 78, 1, 96, 26, 45, 47],
    [60, 54, 81, 66, 81, 90, 80],
    [70, 5, 46, 14, 71, 19, 66],
]
col_headers = ['week', 'week1', 'week2', 'week3',
               'week4', 'week5', 'week6', 'week7']
row_headers = ['用户{}'.format(i) for i in range(1, 11)]





import csv,os


def write_csv(csv_file, headers, rows):
    f = open(csv_file, 'wt')
    writer = csv.writer(f)
    writer.writerow(headers)
    for index, row in enumerate(rows):
        writer.writerow([row_headers[index]] + row)
    f.close()

@flask_app.route('/email')
def email():
    csv_file = os.path.join('C:\\Users\\scott\\Documents\\GitHub\\platform\\app', 'statistics.csv')
    write_csv(csv_file, col_headers, rows_data)
    content = render_template('mail/panda.html',col_headers=col_headers,
               row_headers=row_headers,
               rows_data=rows_data)
    
    send_email(['scottcho@qq.com'], content, '测试', '测试组',attachments=[csv_file],nick_from='平台')
    
    return content