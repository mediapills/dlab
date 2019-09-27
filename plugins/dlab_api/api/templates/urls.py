from flask import Blueprint
from flask_restful import Api

from api.templates.views import TemplateAPI

template_bp = Blueprint('template', __name__, url_prefix='/template')

api = Api(template_bp)

api.add_resource(TemplateAPI, '/<string:type>')
