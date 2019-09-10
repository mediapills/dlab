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
import abc
import argparse
from abc import abstractmethod

import six

from dlab_core.domain.exceptions import DLabException

TERRAFORM_INIT = 'terraform init'
TERRAFORM_VALIDATE = 'terraform validate'
TERRAFORM_OUTPUT = 'terraform output {} {}'
TERRAFORM_APPLY = 'terraform apply -auto-approve {} {}'
TERRAFORM_DESTROY = 'terraform destroy -auto-approve {} {}'


@six.add_metaclass(abc.ABCMeta)
class BaseIACProvider(object):

    @abc.abstractmethod
    def initialize(self):
        raise NotImplementedError

    @abc.abstractmethod
    def validate(self):
        raise NotImplementedError

    @abc.abstractmethod
    def apply(self):
        raise NotImplementedError

    @abc.abstractmethod
    def destroy(self):
        raise NotImplementedError


class TerraformProviderError(DLabException):
    """
    Raises errors while terraform provision
    """
    pass


class TerraformProvider(BaseIACProvider):
    def __init__(self, executor):
        """
        :param executor: console executor (local console or remote fabric)
        """
        self._console_executor = executor

    @staticmethod
    def extract_args(cli_args):
        args = []
        for key, value in cli_args.items():
            if not value:
                continue
            if type(value) == list:
                quoted_list = ['"{}"'.format(item) for item in value]
                joined_values = ', '.join(quoted_list)
                value = '[{}]'.format(joined_values)
            args.append((key, value))
        return args

    def get_tf_var_string(self, cli_args):
        """Convert dict of cli argument into string of tf var

        :type cli_args: dict
        :param cli_args: dict of cli arguments

        :rtype: str
        :return string of joined "-var 'key=values'"
        """
        args = self.extract_args(cli_args)
        args = ["-var '{0}={1}'".format(key, value) for key, value in args]
        return ' '.join(args)

    def get_tf_args_string(self, cli_args):
        """Convert dict of cli argument into string of tf args

        :type cli_args: dict
        :param cli_args: dict of cli arguments

        :rtype: str
        :return string of joined 'key=values'
        """

        args = self.extract_args(cli_args)
        args = ["-{0} {1}".format(key, value) for key, value in args]
        return ' '.join(args)

    def initialize(self):
        """Initialize terraform

        :raise TerraformProviderError: if initialization was not succeed
        """
        success_message = 'Terraform has been successfully initialized!'
        result = self._console_executor(TERRAFORM_INIT)
        if success_message not in result:
            raise TerraformProviderError(result)

    def validate(self):
        """Validate terraform

        :raise TerraformProviderError: if validation status was not succeed

        """
        success_message = 'Success!'
        result = self._console_executor(TERRAFORM_VALIDATE)
        if success_message not in result:
            raise TerraformProviderError(result)

    def apply(self, tf_params={}, tf_vars={}):
        """Apply terraform

        :type tf_params: dict
        :param tf_params: dict of tf params

        :type tf_vars: dict
        :param tf_vars: dict of tf variables
        """

        vars_str = self.get_tf_var_string(tf_vars)
        params_str = self.get_tf_args_string(tf_params)
        command = TERRAFORM_APPLY.format(params_str, vars_str)
        self._console_executor(command)

    def destroy(self, tf_params={}, tf_vars={}):
        """Destroy terraform

        :type tf_params: dict
        :param tf_params: dict of tf params

        :type tf_vars: dict
        :param tf_vars: dict of tf variables
        """

        vars_str = self.get_tf_var_string(tf_vars)
        params_str = self.get_tf_args_string(tf_params)
        command = TERRAFORM_DESTROY.format(params_str, vars_str)
        self._console_executor(command)

    def output(self, tf_params={}, *cli_args):
        """Get terraform output

        :type tf_params: dict
        :param tf_params: dict of tf params

        :type cli_args: iterable
        :param cli_args: sequence of output args

        :rtype: str
        :return terraform output result
        """
        params = self.get_tf_args_string(tf_params)
        command = TERRAFORM_OUTPUT.format(params, ' '.join(cli_args))
        return self._console_executor(command)


@six.add_metaclass(abc.ABCMeta)
class BaseSourceProvider(object):

    @property
    @abstractmethod
    def terraform_location(self):
        """ get Terraform location
        :rtype:  str
        :return: Terraform location
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def cli_args(self):
        """Get cli arguments

        :rtype:  dict
        :return: dictionary of client arguments
                 with name as key and props as value
        """
        raise NotImplementedError

    def parse_args(self):
        """Get dict of arguments
        :rtype:  dict
        :return: dictionary of cli arguments
        """
        parsers = {}
        for group, args in self.cli_args.items():
            parser = argparse.ArgumentParser()
            for arg in args:
                parser.add_argument(arg['key'], **arg['params'])
            parsers[group] = vars(parser.parse_known_args()[0])
        return parsers
