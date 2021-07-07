from flask_rest_jsonapi import ResourceList, ResourceRelationship

from app import db
from app.apis.v2 import api
from app.apis.v2.auth import auth_required
from app.apis.v2.schemas.cmdb import (AgreementSchema, CredenceSchema,
                                      LinkSchema, ServerGroupSchema,
                                      ServerSchema)
from app.models.cmdb import Agreement, Credence, Link, Server, ServerGroup

from . import BaseResourceDetail


# Create resource managers
class ServerList(ResourceList):
    decorators = (auth_required, )
    schema = ServerSchema
    data_layer = {'session': db.session, 'model': Server}


class ServerDetail(BaseResourceDetail):
    decorators = (auth_required, )
    schema = ServerSchema
    data_layer = {'session': db.session, 'model': Server}


class ServerRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = ServerSchema
    data_layer = {'session': db.session, 'model': Server}


#　服务器分组
class ServerGroupList(ResourceList):
    decorators = (auth_required, )
    schema = ServerGroupSchema
    data_layer = {'session': db.session, 'model': ServerGroup}


class ServerGroupDetail(BaseResourceDetail):
    decorators = (auth_required, )
    schema = ServerGroupSchema
    data_layer = {'session': db.session, 'model': ServerGroup}


class ServerGroupRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = ServerGroupSchema
    data_layer = {'session': db.session, 'model': ServerGroup}


# 凭证
class CredenceList(ResourceList):
    decorators = (auth_required, )
    schema = CredenceSchema
    data_layer = {'session': db.session, 'model': Credence}


class CredenceDetail(BaseResourceDetail):
    decorators = (auth_required, )
    schema = CredenceSchema
    data_layer = {'session': db.session, 'model': Credence}


class CredenceRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = CredenceSchema
    data_layer = {'session': db.session, 'model': Credence}


class AgreementList(ResourceList):
    schema = AgreementSchema
    data_layer = {'session': db.session, 'model': Agreement}


class AgreementDetail(BaseResourceDetail):
    decorators = (auth_required, )
    schema = AgreementSchema
    data_layer = {'session': db.session, 'model': Agreement}


class AgreementRelationship(ResourceRelationship):
    decorators = (auth_required, )
    schema = AgreementSchema
    data_layer = {'session': db.session, 'model': Agreement}


# 凭证
class LinkList(ResourceList):
    decorators = (auth_required, )
    schema = LinkSchema
    data_layer = {'session': db.session, 'model': Link}


class LinkDetail(BaseResourceDetail):
    decorators = (auth_required, )
    schema = CredenceSchema
    data_layer = {'session': db.session, 'model': Link}


# Create endpoints
# 服务器

api.route(ServerList, 'server_list', '/api/servers')
api.route(ServerDetail, 'server_detail', '/api/servers/<id>')
api.route(ServerRelationship, 'server_credence',
          '/api/servers/<int:id>/relationships/credence')
api.route(ServerRelationship, 'server_groups',
          '/api/servers/<int:id>/relationships/groups')

# 服务器分组
api.route(ServerGroupList, 'server_group_list', '/api/server_groups')
api.route(ServerGroupDetail, 'server_group_detail', '/api/servers/<id>')
api.route(ServerGroupRelationship, 'group_servers',
          '/api/groups/<int:id>/relationships/servers')

# 凭证
api.route(CredenceList, 'credence_list', '/api/credences')
api.route(CredenceDetail, 'credence_detail', '/api/credences/<id>')
api.route(CredenceRelationship, 'credence_servers',
          '/api/credences/<int:id>/relationships/servers')
api.route(CredenceRelationship, 'credence_agreement',
          '/api/credences/<int:id>/relationships/agreement')

# 协议
api.route(AgreementList, 'agreement_list', '/api/agreements')
api.route(AgreementDetail, 'agreement_detail', '/api/agreements/<id>')
api.route(AgreementRelationship, 'agreement_credences',
          '/api/agreements/<int:id>/relationships/credences')

# Link
api.route(LinkList,
          'link_list',
          '/api/links',
          url_rule_options={'methods': [
              'GET',
          ]})
api.route(LinkDetail,
          'link_detail',
          '/api/links/<id>',
          url_rule_options={'methods': [
              'GET',
          ]})
