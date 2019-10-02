from flask import request
from flask_restful import Resource

from api.processes_manager import Manager
from dlab_templates.infrastructure.controllers import APITemplatesController


class TemplateAPI(Resource):

    def get(self, type):
        return APITemplatesController.get_templates(type)

    # TODO: remove after test
    def post(self, type):
        data = request.json
        m = Manager()
        id = m.create_record(data)
        return {'id': id}

