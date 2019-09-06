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
from setuptools import setup

from dlab_core.setup import SetupParametersBuilder, SetupParametersDirector

""" Distribution name of package"""
NAME = 'dlab_deployment'

"""Short summary of the package"""
DESCRIPTION = 'This is a DLab plugin that implements deployment flows.'


class DeploySetupParametersBuilder(SetupParametersBuilder):

    @property
    def entry_points(self):
        deploy_entry_points = {
            "dlab.plugin.cli": [
                "deployment = dlab_deployment.plugins:DeploymentCLIPlugin",
            ],
            "dlab.plugin.api": [
                "deployment = dlab_deployment.plugins:DeploymentAPIPlugin",
            ],
        }
        return dict(super(DeploySetupParametersBuilder, self).entry_points,
                    **deploy_entry_points)


def do_setup():
    builder = DeploySetupParametersBuilder(NAME, DESCRIPTION)
    director = SetupParametersDirector()
    director.build(builder)
    args = director.parameters

    setup(**args)


if __name__ == "__main__":
    do_setup()
