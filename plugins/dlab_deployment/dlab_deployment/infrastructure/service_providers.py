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
import json

from dlab_deployment.domain.service_providers import BaseIaCServiceProvider
from dlab_deployment.infrastructure.terraform import Terraform


class TerraformServiceProvider(BaseIaCServiceProvider):

    def __init__(self, command_executor, **kwargs):
        """
        :type command_executor:  BaseCommandExecutor
        :param command_executor: Command Line Executor
        :type parameters:  dict
        :param parameters: CLI arguments
        """

        self.terraform = Terraform(command_executor, **kwargs)

    def provision(self):
        """Provision terraform"""

        self.terraform.initialize()
        self.terraform.validate()
        self.terraform.apply()

    def destroy(self):
        """Deploy terraform"""

        self.terraform.initialize()
        self.terraform.validate()
        self.terraform.destroy()

    def output(self):
        """Extract terraform output
        :rtype dict
        """

        return {k: v.get('value') for k, v in
                json.loads(self.terraform.output()).items()}
