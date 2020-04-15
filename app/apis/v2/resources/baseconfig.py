# -*- coding: utf-8 -*-


from flask_rest_jsonapi import (Api, ResourceDetail, ResourceList,
                                ResourceRelationship)

from app import db
from app.apis.v2 import api
from app.apis.v2.auth import auth_required
from app.apis.v2.schemas.baseconfig import StatusSchema, TagSchema
from app.models.baseconfig import Status, Tag


# 问题状态
class StatusList(ResourceList):
    
    decorators = (auth_required,)
    schema = StatusSchema
    data_layer = {'session': db.session,
                  'model': Status
                }

class StatusDetail(ResourceDetail):
    decorators = (auth_required,)

    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id':id})
                self._data_layer.delete_object(obj, {'id':id})

    schema = StatusSchema
    data_layer = {'session': db.session,
                  'model': Status  
                }

class StatusRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = StatusSchema
    data_layer = {'session': db.session,
                  'model': Status}

#　问题标签
class TagList(ResourceList):
    
    decorators = (auth_required,)
    schema = TagSchema
    data_layer = {'session': db.session,
                  'model': Tag
                }

class TagDetail(ResourceDetail):
    decorators = (auth_required,)

    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id':id})
                self._data_layer.delete_object(obj, {'id':id})

    schema = TagSchema
    data_layer = {'session': db.session,
                  'model': Tag 
                }

class TagRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = TagSchema
    data_layer = {'session': db.session,
                  'model': Tag
                  }


#状态
api.route(StatusList, 'status_list', '/api/status')
api.route(StatusDetail, 'status_detail', '/api/status/<id>')
api.route(StatusRelationship, 'status_requirements', '/api/status/<int:id>/relationships/issue_requirements')
api.route(StatusRelationship, 'status_bugs', '/api/status/<int:id>/relationships/issue_bugs')
api.route(StatusRelationship, 'status_tasks', '/api/status/<int:id>/relationships/issue_tasks')
api.route(StatusRelationship, 'status_baselines', '/api/status/<int:id>/relationships/baselines')

# 问题标签
api.route(TagList, 'tag_list', '/api/tags')
api.route(TagDetail, 'tag_detail', '/api/tags/<id>')
api.route(TagRelationship, 'tag_requirements', '/api/tag/<int:id>/relationships/issue_requirements')
api.route(TagRelationship, 'tag_bugs', '/api/tag/<int:id>/relationships/issue_bugs')
api.route(TagRelationship, 'tag_tasks', '/api/tag/<int:id>/relationships/tasks')
