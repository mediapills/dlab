from flask import request
from flask_restful import Resource

from dlab_deployment.infrastructure.controllers import APIProjectsController


class CreateProjectAPI(Resource):

    def post(self):
        return APIProjectsController.create_project(request)


class ProjectAPI(Resource):

    def get(self, id, **kwargs):
        return APIProjectsController.get_project(id)

    def put(self, name, **kwargs):
        return APIProjectsController.update_project(name, **kwargs)

    def delete(self, name, **kwargs):
        return APIProjectsController.delete_project(name)
