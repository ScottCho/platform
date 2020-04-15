from decimal import Decimal

from flask import jsonify, request
from flask.views import MethodView

from app import db
from app.apis.v2 import api_v2


class StatAPI(MethodView):
    def get(self):

        # 每个开发基线更新的总次数及总的基线数
        developer_relase_stmt = db.text(
            "SELECT username, sum( updateno ) as update_total, count(baselines.id) AS baseline_total FROM baselines,users where users.id=baselines.developer_id GROUP BY developer_id")
        # 每个项目更新基线总的次数及总的基线数
        project_relase_stmt = db.text("SELECT project_name,sum( updateno ) AS proejct_relase_total,count( baseline_id ) FROM (SELECT projects.id AS project_id,projects.NAME AS project_name,apps.id AS app_id FROM apps,projects WHERE apps.project_id = projects.id ) t1 JOIN ( SELECT id AS baseline_id,app_id,updateno FROM baselines ) t2 ON t1.app_id = t2.app_id GROUP BY project_id")

        # 执行sql
        developer_relase_result = db.session.execute(developer_relase_stmt).fetchall()
        project_relase_result = db.session.execute(project_relase_stmt).fetchall()
        db.session.close()

        # 开发每条基线的平均发布次数
        developer_releases_per_baseline = [(developer, round(int(update_total)/baseline_toatl, 2))
                                           for developer, update_total, baseline_toatl in developer_relase_result]
        # 项目每条基线的平均发布次数
        project_releases_per_baseline = [(project, round(int(update_total)/baseline_toatl, 2))
                                         for project, update_total, baseline_toatl in project_relase_result]

        # 结果处理成json数据
        return(jsonify(data=[
            {"type": "devloper_releases_per_baseline",
                "attribute": dict(developer_releases_per_baseline)},
            {"type": "project_releases_per_baseline",
             "attribute": dict(project_releases_per_baseline)},
        ]
        )
        )


api_v2.add_url_rule('/stat', view_func=StatAPI.as_view('stat'), methods=['GET', ])
