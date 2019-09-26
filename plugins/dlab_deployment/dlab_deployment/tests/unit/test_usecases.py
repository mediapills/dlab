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

from dlab_core.domain.usecases import UseCaseException
from dlab_deployment.domain.service_providers import BaseIaCServiceProvider
from dlab_deployment.domain.usecases import ProvisionUseCase, DestroyUseCase

MOCK_PROVIDER = type(
    'iac_provider', (BaseIaCServiceProvider,),
    {'provision': MagicMock(), 'destroy': MagicMock(),
     'output': MagicMock()})()


class TestDeploymentUseCase(unittest.TestCase):
    def test_invalid_iac_provider(self):
        invalid_providers = ['', {}, [], (), None, 0]
        for provider in invalid_providers:
            with self.assertRaises(UseCaseException):
                ProvisionUseCase(provider)


class TestProvisionUseCase(unittest.TestCase):
    def test_execute(self):
        ProvisionUseCase(MOCK_PROVIDER).execute()
        MOCK_PROVIDER.provision.assert_called()


class TestDestroyUseCase(unittest.TestCase):
    def test_execute(self):
        DestroyUseCase(MOCK_PROVIDER).execute()
        MOCK_PROVIDER.destroy.assert_called()
