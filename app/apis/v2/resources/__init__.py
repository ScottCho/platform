'''
@Author: your name
@Date: 2020-04-29 18:39:10
@LastEditTime: 2020-04-29 18:41:19
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /platform/app/apis/v2/resources/__init__.py
'''
from flask_rest_jsonapi import ResourceDetail


class BaseResourceDetail(ResourceDetail):
    # 改写成批量删除，kwargs={'id':'[1,2,3]'}或者 kwargs={'id':1}
    # 支持两种方式删除
    def delete_object(self, kwargs):
        ids = kwargs.get('id')
        if ids[0] != '[':
            obj = self._data_layer.get_object(kwargs)
            self._data_layer.delete_object(obj, kwargs)
        else:
            for id in ids[1:-1].split(','):
                obj = self._data_layer.get_object({'id': id})
                self._data_layer.delete_object(obj, {'id': id})
