from flask import Blueprint
from flask_restful import Api

from dlab_core.plugins import BaseAPIPlugin
from dlab_notebooks.infrastructure.views import (CreateNotebookAPI,
                                                 NotebookAPI,
                                                 NotebookProjectLibAPI,
                                                 NotebookLibAPI)

notebook_bp = Blueprint('notebook', __name__, url_prefix='/notebook')

api = Api(notebook_bp)


class NotebookAPIPlugin(BaseAPIPlugin):

    @staticmethod
    def add_routes(app):
        api.add_resource(CreateNotebookAPI, '', methods=['POST'])
        api.add_resource(NotebookAPI,
                         '/<string:project>/<string:name>/status',
                         '/<string:project>/<string:name>',
                         '/<string:project>/<string:name>/<string:action>'
                         )
        api.add_resource(NotebookProjectLibAPI,
                         '/<string:project>/<string:name>/lib'
                         )
        api.add_resource(NotebookLibAPI, '/<string:type>')
        app.register_blueprint(notebook_bp)
