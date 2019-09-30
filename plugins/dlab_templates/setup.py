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
from dlab_core.setup import (SetupParametersBuilder,
                             SetupParametersDirector,
                             VERSION_FILE)

""" Distribution name of package"""
NAME = 'dlab_templates'

"""Short summary of the package"""
DESCRIPTION = 'This a provider to API support.'


class APISetupParametersBuilder(SetupParametersBuilder):

    @property
    def entry_points(self):
        api_entry_points = {
            "dlab.plugin.api": [
                "templates = dlab_templates.plugins:TemplateAPIPlugin",
            ],
        }
        return dict(super(APISetupParametersBuilder, self).entry_points,
                    **api_entry_points)


def do_setup():
    builder = APISetupParametersBuilder(NAME, DESCRIPTION)
    director = SetupParametersDirector()
    director.build(builder)
    args = director.parameters
    setup(**args)


if __name__ == "__main__":
    do_setup()
