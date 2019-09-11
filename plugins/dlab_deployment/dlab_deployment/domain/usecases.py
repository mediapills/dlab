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
from dlab_core.domain.usecases import BaseUseCase


class DeployUseCase(BaseUseCase):

    def __init__(self, iac_provider, deployment_provider):
        """
        :type iac_provider: BaseIACProvider
        :param iac_provider: Infrastructure as Code provider

        :type deployment_provider: BaseDeploymentProvider
        :param deployment_provider:
        """
        self.iac_provider = iac_provider
        self.deployment_provider = deployment_provider

    def execute(self):
        self.iac_provider.initialize()
        self.iac_provider.validate()
        self.iac_provider.deploy()
        self.deployment_provider.configure()


class DestroyUseCase(BaseUseCase):

    def __init__(self, iac_provider):
        """
        :type iac_provider: BaseIACProvider
        :param iac_provider:Infrastructure as Code provider
        """
        self.iac_provider = iac_provider

    def execute(self):
        self.iac_provider.initialize()
        self.iac_provider.validate()
        self.iac_provider.destroy()
