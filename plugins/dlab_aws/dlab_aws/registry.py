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
from dlab_core.registry import register_context

"""Plugin public name."""
PLUGIN_PREFIX = "aws"


class AWSCliHandler(BaseCliHandler):

    def parse_args(self):
        available_targets = ['endpoint', 'k8s']
        usage = 'usage: dlab deploy aws {}\n'.format(available_targets)
        target = len(sys.argv) > 3 and sys.argv[3]

        if target in self.HELP_OPTIONS:
            sys.stdout.write(usage)
            exit(0)

        if not target or target not in available_targets:
            sys.stderr.write(usage)
            exit(1)
        sys.stdout.write('Success\n')


def bootstrap():
    """Bootstrap AWS Plugin"""
    register_context('aws.deploy.cli.parser', lambda c: AWSCliHandler().execute)
