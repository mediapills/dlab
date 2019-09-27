from flask_restful import Resource

from dlab_templates.infrastructure.controllers import APITemplatesController


class TemplateAPI(Resource):

    def get(self, type):
        return APITemplatesController.get_templates(type)
