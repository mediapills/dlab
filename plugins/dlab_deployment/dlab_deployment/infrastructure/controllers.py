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
# *****************************************************************************
import subprocess
import sys

from dlab_core.infrastructure.controllers import BaseCLIController
from dlab_core.providers import TerraformProvider
from dlab_deployment.infrastructure.services import DeploymentService


class BaseDeploymentCLIController(BaseCLIController):

    @classmethod
    def deploy(cls, provider):
        """
        :type provider: BaseSourceProvider
        :param provider: Source provider
        """
        tf_provider = TerraformProvider(
            lambda c: cls.console_execute(c, provider.terraform_location))
        DeploymentService.deploy(tf_provider, provider)

    @classmethod
    def destroy(cls, provider):
        """
        :type provider: BaseSourceProvider
        :param provider: Source provider
        """
        tf_provider = TerraformProvider(
            lambda c: cls.console_execute(c, provider.terraform_location))
        DeploymentService.destroy(tf_provider, provider)

    @staticmethod
    def console_execute(command, location):
        """Execute command from certain location
        :type command: str
        :param command: console command
        :type location: str
        :param location: path to terraform files

        :rtype str
        :return: execution output
        """
        lines = []
        process = subprocess.Popen(
            command, shell=True, cwd=location, universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = process.stdout.readline()
            lines.append(line)
            # TODO: Add logging
            if line == '' and process.poll() is not None:
                break
            if 'error' in line.lower():
                sys.exit(0)
        return ''.join(lines)
