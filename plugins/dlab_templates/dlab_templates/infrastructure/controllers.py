from dlab_core.infrastructure.controllers import BaseAPIController


class APITemplatesController(BaseAPIController):
    allowed_types = ['exploratory', 'computational']

    @classmethod
    def get_templates(cls, type):
        if type not in cls.allowed_types:
            return {"code": 0, "message": "string"}, 400
        return {}, 200
