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

from mock import patch

from dlab_aws.infrastructure.controllers import deployment
from dlab_aws.infrastructure.controllers.deployment import AWSCLIController
from dlab_deployment.domain.service_providers import BaseIaCServiceProvider


class TestController(unittest.TestCase):
    @patch.object(deployment, 'SSNDestroyUseCase')
    def test_destroy_ssn(self, destroy_use_case_mock):
        AWSCLIController.destroy_ssn([])
        destroy_use_case_mock.assert_called()

    @patch.object(deployment, 'TerraformServiceProvider',
                  spec=BaseIaCServiceProvider)
    @patch.object(deployment, 'SSNConfigurationUseCase')
    def test_deploy_ssn(self, configuration_usecase, service_provider):
        with patch.object(deployment, 'ParamikoCommandExecutor'):
            AWSCLIController.deploy_ssn([])
            service_provider().provision.assert_called()
            configuration_usecase().execute.assert_called()

    @patch.object(deployment, 'EndpointDestroyUseCase')
    def test_destroy_endpoint(self, destroy_use_case_mock):
        AWSCLIController.destroy_endpoint([])
        destroy_use_case_mock.assert_called()

    @patch.object(deployment, 'TerraformServiceProvider',
                  spec=BaseIaCServiceProvider)
    @patch.object(deployment, 'EndpointConfigurationUseCase')
    @patch.object(deployment, 'SSNConfigurationUseCase')
    def test_deploy_endpoint(self, ssn_configuration_usecase,
                             configuration_usecase, service_provider):
        with patch.object(deployment, 'ParamikoCommandExecutor'):
            AWSCLIController.deploy_endpoint([])
            ssn_configuration_usecase().execute.ssn_configuration_usecase()
            service_provider().provision.assert_called()
            configuration_usecase().execute.assert_called()

    @patch.object(deployment, 'ProjectDestroyUseCase')
    def test_destroy_project(self, destroy_use_case_mock):
        AWSCLIController.destroy_project([])
        destroy_use_case_mock.assert_called()

    @patch.object(deployment, 'TerraformServiceProvider',
                  spec=BaseIaCServiceProvider)
    def test_deploy_project(self, service_provider):
        with patch.object(deployment, 'ParamikoCommandExecutor'):
            AWSCLIController.deploy_project([])
            service_provider().provision.assert_called()
