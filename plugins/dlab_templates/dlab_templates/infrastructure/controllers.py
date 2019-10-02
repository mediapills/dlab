from dlab_core.domain.entities import STATUS_OK, STATUS_BAD_REQUEST
from dlab_core.infrastructure.controllers import BaseAPIController

EXPLORATORY = 'exploratory'
COMPUTATIONAL = 'computational'


class APITemplatesController(BaseAPIController):
    allowed_types = [EXPLORATORY, COMPUTATIONAL]

    @classmethod
    def get_templates(cls, type):
        if type not in cls.allowed_types:
            return {"code": 0, "message": "string"}, STATUS_BAD_REQUEST
        return {}, STATUS_OK
