from dlab_core.domain.entities import STATUS_BAD_REQUEST, STATUS_PROCESSED
from dlab_core.infrastructure.controllers import BaseAPIController
from dlab_core.infrastructure.schema_validator import validate_schema
from dlab_notebooks.infrastructure.schemas import (CREATE_NOTEBOOK_SCHEMA,
                                                   INSTALL_LIB_SCHEMA)

START = 'start'
STOP = 'stop'
JUPYTER = 'jupyter'
RSTUDIO = 'rstudio'
TENSOR = 'tensor'
ZEPPELIN = 'zeppelin'
JUPYTER_TENSOR = 'jupyter_tensor'
RSTUDIO_TENSOR = 'rstudio_tensor'
DEEP_LEARNING = 'deep_learning'


class APINotebooksController(BaseAPIController):
    allowed_actions = [START, STOP]

    @classmethod
    def create_notebook(cls, data):
        is_valid = validate_schema(data, CREATE_NOTEBOOK_SCHEMA)
        if is_valid:
            return {'code': is_valid}, STATUS_PROCESSED

        return {"code": is_valid, "message": "string"}, STATUS_BAD_REQUEST

    @classmethod
    def get_notebook(cls, project, name):
        return {"status": "running", "error_message": "string"}

    @classmethod
    def update_notebook(cls, project, name, **kwargs):
        action = kwargs.get('action')
        if action not in cls.allowed_actions:
            return {"code": 0, "message": "string"}, STATUS_BAD_REQUEST

        # TODO: handle not found
        # if not found:
        #     return {"code": 0, "message": "string"}, 404

        status = cls.do_action(action)
        return {'status': status}, STATUS_PROCESSED

    @classmethod
    def delete_notebook(cls, project, name):
        # TODO: handle not found
        # if not found:
        #     return {"code": 0, "message": "string"}, 404
        return {}, STATUS_PROCESSED

    @classmethod
    def do_action(cls, action):
        status = 1
        if action == START:
            pass
        if action == STOP:
            pass
        return status


class APINotebookProjectLibController(BaseAPIController):

    @classmethod
    def get_installed_libs_for_notebook(cls, project, name):
        return {}

    @classmethod
    def install_libs_for_notebook(cls, project, name, data):
        is_valid = validate_schema(data, INSTALL_LIB_SCHEMA)
        if is_valid:
            return {'code': is_valid}, STATUS_PROCESSED

        return {"code": is_valid, "message": "string"}, STATUS_BAD_REQUEST


class APINotebookLibController(BaseAPIController):
    allowed_types = [JUPYTER, RSTUDIO, TENSOR, ZEPPELIN,
                     JUPYTER_TENSOR, RSTUDIO_TENSOR, DEEP_LEARNING]

    @classmethod
    def get_available_libs(cls, type):
        if type not in cls.allowed_types:
            return {"code": 0, "message": "string"}, STATUS_BAD_REQUEST
        return {}
