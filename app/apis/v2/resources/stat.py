#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: Zhao Yong
# FILE: /Code/githup/platform/app/apis/v2/resources/stat.py
# DATE: 2020/04/29 Wed
# TIME: 19:05:31

# DESCRIPTION:

import json

from flask import Response
from flask.views import MethodView
from pyecharts import options as opts
from pyecharts.charts import Bar

from app import db, redis_cli
from app.apis.v2 import api_v2
from app.apis.v2.auth import auth_required


def bar_base() -> Bar:
    # 每个项目更新基线总的次数及总的基线数
    project_relase_stmt = db.text(
        "SELECT project_name,sum( updateno ) AS proejct_relase_total,count( baseline_id ) FROM (SELECT projects.id AS project_id,projects.NAME AS project_name,apps.id AS app_id FROM apps,projects WHERE apps.project_id = projects.id ) t1 JOIN ( SELECT id AS baseline_id,app_id,updateno FROM baselines ) t2 ON t1.app_id = t2.app_id GROUP BY project_id"
    )

    # 执行sql
    project_relase_result = db.session.execute(project_relase_stmt).fetchall()
    db.session.close()

    # 项目每条基线的平均发布次数
    project_releases_per_baseline = [
        (project, round(int(update_total) / baseline_toatl, 2))
        for project, update_total, baseline_toatl in project_relase_result
    ]
    c = (Bar().add_xaxis(list(
        dict(project_releases_per_baseline).keys())).add_yaxis(
            "项目", list(
                dict(project_releases_per_baseline).values())).set_global_opts(
                    title_opts=opts.TitleOpts(title="基线平均发布次数", subtitle="项目"))
         )
    return c


@api_v2.route("/echarts")
def get_bar_chart():
    c = bar_base()
    return c.dump_options_with_quotes()


class StatAPI(MethodView):
    def get(self):

        # 每个开发基线更新的总次数及总的基线数
        developer_relase_stmt = db.text(
            "SELECT username, sum( updateno ) as update_total, count(baselines.id) AS baseline_total FROM baselines,users where users.id=baselines.developer_id GROUP BY developer_id"
        )
        # 每个项目更新基线总的次数及总的基线数
        project_relase_stmt = db.text(
            "SELECT project_name,sum( updateno ) AS proejct_relase_total,count( baseline_id ) FROM (SELECT projects.id AS project_id,projects.NAME AS project_name,apps.id AS app_id FROM apps,projects WHERE apps.project_id = projects.id ) t1 JOIN ( SELECT id AS baseline_id,app_id,updateno FROM baselines ) t2 ON t1.app_id = t2.app_id GROUP BY project_id"
        )

        # 执行sql
        developer_relase_result = db.session.execute(
            developer_relase_stmt).fetchall()
        project_relase_result = db.session.execute(
            project_relase_stmt).fetchall()
        db.session.close()

        # 开发每条基线的平均发布次数
        developer_releases_per_baseline = [
            (developer, round(int(update_total) / baseline_toatl, 2)) for
            developer, update_total, baseline_toatl in developer_relase_result
        ]
        # 项目每条基线的平均发布次数
        project_releases_per_baseline = [
            (project, round(int(update_total) / baseline_toatl, 2))
            for project, update_total, baseline_toatl in project_relase_result
        ]

        developer_releases_per_baseline = sorted(
            dict(developer_releases_per_baseline).items(),
            key=lambda item: item[1],
            reverse=True)[0:10]

        # 系统动态
        redis_cli.ltrim('frog_list', 0, 100)
        dynamics = redis_cli.lrange('frog_list', 0, 9)
        # 结果处理成json数据
        return (Response(json.dumps({
            'data': [
                {
                    "type": "devloper_releases_per_baseline",
                    "attribute": dict(developer_releases_per_baseline)
                },
                {
                    "type": "project_releases_per_baseline",
                    "attribute": dict(project_releases_per_baseline)
                },
                {
                    "type": "dynamics",
                    "attribute": dynamics
                }
            ]
        }),
                         mimetype='application/json'))


api_v2.add_url_rule('/stat',
                    view_func=StatAPI.as_view('stat'),
                    methods=[
                        'GET',
                    ])
