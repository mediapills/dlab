from flask import request
from flask_restful import Resource

from dlab_notebooks.infrastructure.controllers import (
    APINotebooksController,
    APINotebookProjectLibController,
    APINotebookLibController)


class CreateNotebookAPI(Resource):

    def post(self):
        return APINotebooksController.create_notebook(request.json)


# TODO: maybe add base View
class NotebookAPI(Resource):

    def get(self, project, name, **kwargs):
        return APINotebooksController.get_notebook(project, name)

    def put(self, project, name, **kwargs):
        return APINotebooksController.update_notebook(project, name, **kwargs)

    def delete(self, project, name, **kwargs):
        return APINotebooksController.delete_notebook(project, name)


class NotebookProjectLibAPI(Resource):

    def get(self, project, name):
        return APINotebookProjectLibController.get_installed_libs_for_notebook(project, name)  # noqa: E501

    def post(self, project, name):
        return APINotebookProjectLibController.install_libs_for_notebook(
            project, name, request.json
        )


class NotebookLibAPI(Resource):

    def get(self, type):
        return APINotebookLibController.get_available_libs(type)
