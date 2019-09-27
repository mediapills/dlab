from flask import Blueprint
from flask_restful import Api

from api.projects.views import CreateProjectAPI, ProjectAPI

project_bp = Blueprint('project', __name__, url_prefix='/project')

api = Api(project_bp)

api.add_resource(CreateProjectAPI, '')
api.add_resource(ProjectAPI,
                 '/<string:name>/status',
                 '/<string:name>',
                 '/<string:name>/<string:action>'
                 )
