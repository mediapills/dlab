from flask import request
from flask_restful import Resource

from api.utils.schema_validator import validate_schema
from api.utils.schemas import CREATE_PROJECT_SCHEMA


class CreateProjectAPI(Resource):

    def post(self):
        is_valid = validate_schema(request.json, CREATE_PROJECT_SCHEMA)
        if is_valid:
            return {'code': is_valid}, 202

        return {"code": is_valid, "message": "string"}, 400


# TODO: maybe add base View
class ProjectAPI(Resource):
    allowed_actions = ['start', 'stop']

    # TODO: check status param needed
    def get(self, name, **kwargs):
        return {"status": "running", "error_message": "string"}

    def put(self, name, **kwargs):
        action = kwargs.get('action')
        if action not in self.allowed_actions:
            return {"code": 0, "message": "string"}, 400

        # TODO: handle not found
        # if not found:
        #     return {"code": 0, "message": "string"}, 404

        status = self.do_action(action)
        return {'status': status}, 202

    def delete(self, name, **kwargs):
        # TODO: handle not found
        # if not found:
        #     return {"code": 0, "message": "string"}, 404
        return {}, 202

    def do_action(self, action):
        status = 1
        if action == 'start':
            pass
        if action == 'stop':
            pass

        return status
