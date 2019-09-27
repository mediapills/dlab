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

from dlab_core.domain.exceptions import DLabException
from dlab_core.domain.helper import (
    LC_ERR_INVALID_PARAMETER_TYPE, validate_property_type)
from dlab_deployment.infrastructure.command_executor import BaseCommandExecutor

"""Terraform commands"""
TERRAFORM_COMMAND = 'terraform '
TERRAFORM_INIT_COMMAND = TERRAFORM_COMMAND + 'init'
TERRAFORM_VALIDATE_COMMAND = TERRAFORM_COMMAND + 'validate'
TERRAFORM_OUTPUT_COMMAND = TERRAFORM_COMMAND + 'output'
TERRAFORM_APPLY_COMMAND = TERRAFORM_COMMAND + 'apply'
TERRAFORM_DESTROY_COMMAND = TERRAFORM_COMMAND + 'destroy'

LC_ERR_TF_PROVISIONING_ERROR_TEMPLATE = 'Exception raised while {}'
TF_INIT_SUCCESS_MSG = 'Terraform has been successfully initialized!'
TF_VALIDATE_SUCCESS_MSG = 'Success!'

ACTIONS = 'actions'
TF_PARAMETER = 'tf_param'
INITIAL_TYPE = 'initial_type'
INITIAL_VALUE = 'initial_value'

APPLY = 1
DESTROY = 2
OUTPUT = 4

TF_COMMANDS_ACTION_CODES = {
    TERRAFORM_APPLY_COMMAND: APPLY,
    TERRAFORM_DESTROY_COMMAND: DESTROY,
    TERRAFORM_OUTPUT_COMMAND: OUTPUT,
}

TERRAFORM_PARAMS = {
    'no_color': {
        INITIAL_TYPE: bool,
        INITIAL_VALUE: True,
        ACTIONS: APPLY | DESTROY,
        TF_PARAMETER: lambda x: '-no-color',
    },
    'auto_approve': {
        INITIAL_TYPE: bool,
        INITIAL_VALUE: True,
        ACTIONS: APPLY | DESTROY,
        TF_PARAMETER: lambda x: '-auto-approve',
    },
    'json_view': {
        INITIAL_TYPE: bool,
        INITIAL_VALUE: True,
        ACTIONS: OUTPUT,
        TF_PARAMETER: lambda x: '-json',
    },
    'state': {
        INITIAL_TYPE: str,
        INITIAL_VALUE: '',
        ACTIONS: APPLY | DESTROY | OUTPUT,
        TF_PARAMETER: lambda x: '-state={}'.format(x),
    },
    'variables': {
        INITIAL_TYPE: dict,
        INITIAL_VALUE: {},
        ACTIONS: APPLY | DESTROY,
        TF_PARAMETER: lambda x: ' '.join(['-var \'{}={}\''.format(k, v)
                                          for k, v in x.items()]),
    },
}


class TerraformException(DLabException):
    pass


def validate_tf_result(check_phrase, error_msg):
    """
    :type check_phrase: str
    :param check_phrase: String that should be included to output
    :type error_msg: str
    :param error_msg: Error message string
    :return: fn execution
    :raise TerraformException if check phrase not in execution result
    """

    def validate(fn):
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            if check_phrase not in result:
                raise TerraformException(
                    LC_ERR_TF_PROVISIONING_ERROR_TEMPLATE.format(error_msg))
            return result

        return wrapper

    return validate


class Terraform(object):
    def __init__(self, command_executor, **kwargs):
        """
        :type command_executor: BaseCommandExecutor
        :param command_executor: CLI executor
        """

        self.command_executor = command_executor
        self.tf_params = {k: self.set_tf_parameter(kwargs.get(k), v)
                          for k, v in TERRAFORM_PARAMS.items()}
        self.tf_path = self.set_tf_parameter(
            kwargs.get('tf_path'), {INITIAL_TYPE: str, INITIAL_VALUE: ''})

    @property
    def command_executor(self):
        """
        :rtype BaseCommandExecutor
        :return: CLI executor
        """

        return self._command_executor

    @command_executor.setter
    @validate_property_type(BaseCommandExecutor)
    def command_executor(self, executor):
        """
        :type executor:BaseCommandExecutor
        :param executor: CLI executor
        """

        self._command_executor = executor

    @validate_tf_result(TF_INIT_SUCCESS_MSG, TERRAFORM_INIT_COMMAND)
    def initialize(self):
        """Initialize terraform
        :raise TerraformException: if initialization was not succeed
        """

        command = self.build_tf_command(TERRAFORM_INIT_COMMAND)
        return self.command_executor.run(command)

    @validate_tf_result(TF_VALIDATE_SUCCESS_MSG, TERRAFORM_VALIDATE_COMMAND)
    def validate(self):
        """Validate terraform

        :raise TerraformException: if validation status was not succeed
        """
        command = self.build_tf_command(TERRAFORM_VALIDATE_COMMAND)
        return self.command_executor.run(command)

    # TODO: Add errors handling or success check
    def apply(self):
        """Apply terraform"""

        command = self.build_tf_command(TERRAFORM_APPLY_COMMAND)
        return self.command_executor.run(command)

    def destroy(self):
        """Destroy terraform"""

        command = self.build_tf_command(TERRAFORM_DESTROY_COMMAND)
        return self.command_executor.run(command)

    def output(self):
        """Extract terraform output"""

        command = self.build_tf_command(TERRAFORM_OUTPUT_COMMAND)
        with self.command_executor.cd(self.tf_path):
            return self.command_executor.run(command)

    def build_tf_command(self, command):
        """Build terraform options string
        Iterate through available tf options.
        Get terraform presentations of each parameter if  value is not false
        and terraform parameter suits to selected action type
        """

        args = [command]
        args.extend([val[TF_PARAMETER](self.tf_params[key])
                     for key, val in TERRAFORM_PARAMS.items()
                     if self.tf_params[key]
                     and TF_COMMANDS_ACTION_CODES.get(command, 0)
                     & val[ACTIONS]])
        args.append(self.tf_path)
        return ' '.join(args)

    @staticmethod
    def set_tf_parameter(arg, expected):
        """
        :param arg: terraform argument
        :param expected: dict with corresponding default value and expected
        type
        :return: default or actual value if passed
        :raise: DLabException if type doesn't match to expected
        """
        if arg is None:
            return expected[INITIAL_VALUE]
        if not isinstance(arg, expected[INITIAL_TYPE]):
            raise DLabException(LC_ERR_INVALID_PARAMETER_TYPE.format(
                arg, type(arg).__name__, expected[INITIAL_TYPE].__name__))
        return arg
