from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship


from  app import flask_app
from app.models.cmdb import Machine, MachineGroub, Agreement, Credence
from app import db

from app.apis.v2 import api
from app.apis.v2.schemas.cmdb import MachineSchema, CredenceSchema, AgreementSchema
from app.apis.v2.auth import auth_required


# Create resource managers
class MachineList(ResourceList):
    decorators = auth_required,
    schema = MachineSchema
    data_layer = {'session': db.session,
                  'model': Machine}

class MachineDetail(ResourceDetail):
    decorators = auth_required,
    schema = MachineSchema
    data_layer = {'session': db.session,
                  'model': Machine}

class MachineRelationship(ResourceRelationship):
    schema = MachineSchema
    data_layer = {'session': db.session,
                  'model': Machine}

class CredenceList(ResourceList):
    schema = CredenceSchema
    data_layer = {'session': db.session,
                  'model': Credence}

class CredenceDetail(ResourceDetail):
    schema = CredenceSchema
    data_layer = {'session': db.session,
                  'model': Credence}

class CredenceRelationship(ResourceRelationship):
    schema = CredenceSchema
    data_layer = {'session': db.session,
                  'model': Credence}


class AgreementList(ResourceList):
    schema = AgreementSchema
    data_layer = {'session': db.session,
                  'model': Agreement}

class AgreementDetail(ResourceDetail):
    schema = AgreementSchema
    data_layer = {'session': db.session,
                  'model': Agreement}

class AgreementRelationship(ResourceRelationship):
    schema = AgreementSchema
    data_layer = {'session': db.session,
                  'model': Agreement}

       
# Create endpoints
api.route(MachineList, 'machine_list', '/api/machines')
api.route(MachineDetail, 'machine_detail', '/api/machines/<int:id>')
api.route(MachineRelationship, 'machine_credence', '/api/machines/<int:id>/relationships/credence')
api.route(CredenceList, 'credence_list', '/api/credences')
api.route(CredenceDetail, 'credence_detail', '/api/credences/<int:id>')
api.route(CredenceRelationship, 'credence_machines', '/api/credences/<int:id>/relationships/machines')
api.route(CredenceRelationship, 'credence_agreement', '/api/credences/<int:id>/relationships/agreement')
api.route(AgreementList, 'agreement_list', '/api/agreements')
api.route(AgreementDetail, 'agreement_detail', '/api/agreements/<int:id>')
api.route(AgreementRelationship, 'agreement_credences', '/api/agreements/<int:id>/relationships/credences')