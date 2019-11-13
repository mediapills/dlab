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
import unittest

from mock import MagicMock

from dlab_deployment.infrastructure.command_executor import BaseCommandExecutor
from dlab_core.domain.usecases import UseCaseException
from dlab_deployment.domain.service_providers import BaseIaCServiceProvider
from dlab_deployment.domain.usecases import (ProvisionUseCase, DestroyUseCase,
                                             SSNConfigurationUseCase)

SSN_CONFIGURATION = 'dlab_deployment.domain.usecases.SSNConfigurationUseCase'


class TestProvisionUseCase(unittest.TestCase):
    def test_execute(self):
        provider = MagicMock(spec=BaseIaCServiceProvider)
        ProvisionUseCase(provider).execute()
        provider.provision.assert_called()


class TestDestroyUseCase(unittest.TestCase):
    def test_execute(self):
        provider = MagicMock(spec=BaseIaCServiceProvider)
        DestroyUseCase(provider).execute()
        provider.destroy.assert_called()


class TestDeploymentUseCase(unittest.TestCase):
    def test_invalid_iac_provider_type(self):
        invalid_providers = ['', {}, [], (), None, 0]
        for provider in invalid_providers:
            with self.assertRaises(UseCaseException):
                ProvisionUseCase(provider)


class TestConfigurationUseCase(unittest.TestCase):

    def setUp(self):
        self.provider = MagicMock(spec=BaseIaCServiceProvider)
        self.command_executor = MagicMock(spec=BaseCommandExecutor)
        self.use_case = SSNConfigurationUseCase(self.provider,
                                                self.command_executor, '', '')

    def test_execute(self):
        self.use_case.check_k8s_status = MagicMock()
        self.use_case.check_tiller_status = MagicMock()
        self.use_case.copy_terraform_to_remote = MagicMock()
        self.provider.provision = MagicMock()
        self.use_case.execute()

        self.use_case.check_k8s_status.assert_called()
        self.use_case.check_tiller_status.assert_called()
        self.use_case.copy_terraform_to_remote.assert_called()
        self.provider.provision.assert_called()

    def test_check_k8s_status(self):
        self.command_executor.run.return_value = '''
        Kubernetes master is running
        KubeDNS is running
        '''
        self.assertEqual(self.use_case.check_k8s_status(), None)

    def test_check_tiller_status(self):
        self.command_executor.run.return_value = 'Running'
        self.assertEqual(self.use_case.check_tiller_status(), None)

    def test_copy_terraform_to_remote(self):
        self.use_case.copy_terraform_to_remote()
        self.command_executor.put.assert_called()
