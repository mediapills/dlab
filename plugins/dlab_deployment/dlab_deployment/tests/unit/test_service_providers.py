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

from mock import patch, MagicMock

from dlab_deployment.infrastructure.service_providers import (
    TerraformServiceProvider)


class TestTerraformServiceProviders(unittest.TestCase):

    def setUp(self):
        tf = 'dlab_deployment.infrastructure.service_providers.Terraform'
        with patch(tf) as mock:
            mock.return_value = MagicMock()
            self.provider = TerraformServiceProvider(None)

    def test_provision(self):
        self.provider.provision()
        self.provider.terraform.initialize.assert_called()
        self.provider.terraform.validate.assert_called()
        self.provider.terraform.apply.assert_called()
        self.provider.terraform.destroy.assert_not_called()

    def test_destroy(self):
        self.provider.destroy()
        self.provider.terraform.initialize.assert_called()
        self.provider.terraform.validate.assert_called()
        self.provider.terraform.destroy.assert_called()
        self.provider.terraform.apply.assert_not_called()

    def test_output(self):
        self.provider.output()
        self.provider.terraform.output.assert_called()
