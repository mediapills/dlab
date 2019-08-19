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
import sys

from dlab_core.clidriver import BaseCliHandler
from dlab_core.registry import (
    register_context, get_resource, CONTAINER_PARAM_PLUGINS)

"""Plugin public name."""
PLUGIN_PREFIX = "deployment"


class DeployCliHandler(BaseCliHandler):
    @property
    def next_handler(self):
        return '{}.deploy.cli.parser'.format(sys.argv[2])

    def parse_args(self):
        providers = ['aws', 'gcp', 'azure']
        usage_template = 'usage: dlab deploy {}\n'
        plugins = get_resource(CONTAINER_PARAM_PLUGINS).keys()
        available_providers = [provider for provider in providers
                               if provider in plugins]
        usage = usage_template.format(available_providers)
        provider = len(sys.argv) > 2 and sys.argv[2]

        if provider in self.HELP_OPTIONS:
            sys.stdout.write(usage)
            exit(0)

        if not provider or provider not in providers:
            sys.stderr.write(usage)
            exit(1)


def bootstrap():
    """Bootstrap Deployment Plugin"""
    register_context('deploy.cli.parser', lambda x: DeployCliHandler().execute)
