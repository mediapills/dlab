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
from dlab_core.domain.exceptions import DLabException
from dlab_deployment.infrastructure.terraform import (
    Terraform, TerraformException, TF_VALIDATE_SUCCESS_MSG,
    TF_INIT_SUCCESS_MSG)


class TestTerraform(unittest.TestCase):

    def setUp(self):
        self.command_executor_mock = MagicMock(spec=BaseCommandExecutor)

    def test_initialize(self):
        self.command_executor_mock.run.return_value = TF_INIT_SUCCESS_MSG
        Terraform(self.command_executor_mock).initialize()
        self.command_executor_mock.run.assert_called_with('terraform init')

    def test_failed_initialize(self):
        self.command_executor_mock.run.return_value = "error"
        with self.assertRaises(TerraformException):
            Terraform(self.command_executor_mock).initialize()

    def test_validate(self):
        self.command_executor_mock.run.return_value = TF_VALIDATE_SUCCESS_MSG
        Terraform(self.command_executor_mock).validate()
        self.command_executor_mock.run.assert_called_with('terraform validate')

    def test_output(self):
        Terraform(self.command_executor_mock).output()
        self.command_executor_mock.run.assert_called_with(
            'terraform output -json ')

    def test_apply(self):
        expected_args = ['terraform', 'apply', '-no-color', '-auto-approve',
                         '-var', "'test=Test'"]
        tf = Terraform(self.command_executor_mock, variables={'test': 'Test'})
        tf.apply()
        self.command_executor_mock.run.assert_called()
        args, kwargs = self.command_executor_mock.run.call_args
        actual_args = [i for arg in args for i in arg.split()]
        self.assertEqual(sorted(actual_args), sorted(expected_args))

    def test_destroy(self):
        expected_args = ['terraform', 'destroy', '-no-color', '-auto-approve',
                         '-var', "'test=Test'"]
        tf = Terraform(self.command_executor_mock, variables={'test': 'Test'})
        tf.destroy()
        self.command_executor_mock.run.assert_called()
        args, kwargs = self.command_executor_mock.run.call_args
        actual_args = [i for arg in args for i in arg.split()]
        self.assertEqual(sorted(actual_args), sorted(expected_args))

    def test_wrong_parameters_type(self):
        with self.assertRaises(DLabException):
            Terraform(self.command_executor_mock, no_color='')

    def test_wrong_command_executor(self):
        types = [str, int, list, dict, set, tuple]
        for executor_type in types:
            with self.assertRaises(DLabException):
                Terraform(MagicMock(spec=executor_type))
