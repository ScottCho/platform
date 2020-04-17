# -*- coding: utf-8 -*-


from flask_rest_jsonapi import (Api, ResourceDetail, ResourceList,
                                ResourceRelationship)

from app import db
from app.apis.v2 import api
from app.apis.v2.auth import auth_required
from app.apis.v2.schemas.baseconfig import (BgtaskSchema, SoftwareSchema,
                                            StatusSchema, TagSchema)
                                        
from app.apis.v2.errors import api_abort
from app.models.baseconfig import Status, Tag, Software, BgTask 
from app.utils.ansible_api import exec_shell,ansible_playbook


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

#　标签
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

#　软件
class SoftwareList(ResourceList):
    
    decorators = (auth_required,)
    schema = SoftwareSchema
    data_layer = {'session': db.session,
                  'model': Software
                }

class SoftwareDetail(ResourceDetail):
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

    schema = SoftwareSchema
    data_layer = {'session': db.session,
                  'model': Software 
                }



#　后台任务
class BgtaskList(ResourceList):
    
    decorators = (auth_required,)

    def after_post(self, result):
        """Hook to make custom work after post method"""
        obj = self._data_layer.get_object({'id':result[0]['data']['id']})
        try:
            message = obj.run_playbook()
        except Exception as e:
            return api_abort(400,detail=str(e))
        else:
            # 返回任务id
            result[0].update({'detail': message})
            return result
            
    schema = BgtaskSchema
    data_layer = {'session': db.session,
                  'model': BgTask
                }


class BgtaskDetail(ResourceDetail):
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

    schema = BgtaskSchema
    data_layer = {'session': db.session,
                  'model': BgTask 
                }
class BgtaskRelationship(ResourceRelationship):
    decorators = (auth_required,)
    schema = BgtaskSchema
    data_layer = {'session': db.session,
                  'model': BgTask}
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

# software
api.route(SoftwareList, 'software_list', '/api/softwares')
api.route(SoftwareDetail, 'software_detail', '/api/softwares/<id>')

# bgtask
api.route(BgtaskList, 'bgtask_list', '/api/bgtasks')
api.route(BgtaskDetail, 'bgtask_detail', '/api/bgtasks/<id>')
api.route(BgtaskRelationship, 'bgtasks_servers', '/api/bgtask/<int:id>/relationships/servers')
