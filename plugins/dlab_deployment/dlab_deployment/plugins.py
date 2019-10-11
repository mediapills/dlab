# *****************************************************************************
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# ******************************************************************************

import abc
import six
from dlab_deployment.infrastructure.views import ProjectAPI, CreateProjectAPI
from flask import Blueprint
from flask_restful import Api

from dlab_core.plugins import BaseAPIPlugin, BaseCLIPlugin

"""deploy entry_points group name for plugins in setup.py"""
DEPLOY_ENTRY_POINTS_GROUP_NAME = 'dlab.deployment.plugin.cli'

project_bp = Blueprint('project', __name__, url_prefix='/project')

api = Api(project_bp)


@six.add_metaclass(abc.ABCMeta)
class BaseDeploymentCLIPlugin(BaseCLIPlugin):
    pass


class DeploymentCLIPlugin(BaseDeploymentCLIPlugin):

    @property
    def ep_group(self):
        return DEPLOY_ENTRY_POINTS_GROUP_NAME

    @property
    def base_routes(self):
        return []


class DeploymentAPIPlugin(BaseAPIPlugin):

    @staticmethod
    def add_routes(app):
        api.add_resource(CreateProjectAPI, '')
        api.add_resource(ProjectAPI,
                         '/<string:id>/status',
                         '/<string:id>',
                         '/<string:name>/<string:action>'
                         )

        app.register_blueprint(project_bp)
