from flask import Blueprint
from flask_restful import Api

from dlab_core.plugins import BaseAPIPlugin
from dlab_templates.infrastructure.views import TemplateAPI

template_bp = Blueprint('template', __name__, url_prefix='/template')

api = Api(template_bp)


class TemplateAPIPlugin(BaseAPIPlugin):

    @staticmethod
    def add_routes(app):
        api.add_resource(TemplateAPI, '/<string:type>')
        app.register_blueprint(template_bp)
