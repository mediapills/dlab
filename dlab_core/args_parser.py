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
import argparse
from itertools import groupby


class ArgumentsBuilder(object):

    def __init__(self):
        self._arguments = []

    def add(self, key, **kwargs):
        """
        :type key: str
        :param key: parameter key
        :type kwargs: dict
        :param kwargs: argument properties dict
        :return: builder
        """
        cli_argument = {
            'key': key,
            'params': kwargs,
        }
        self._arguments.append(cli_argument)
        return self

    def build(self):
        """
        :rtype: list
        :return: list of arguments properties
        """
        return self._arguments


class ArgsParser(object):

    def __init__(self, available_args):
        """
        :type available_args: list
        :param available_args: list of required args
        """

        self.available_args = available_args

    def parse_args(self, user_args):
        """
        :type user_args: list
        :param user_args: list of gotten arguments
        :rtype: dict
        :return: dictionary of arguments
        """

        raise NotImplementedError


class CLIArgsParser(ArgsParser):

    def parse_args(self, user_args=None):
        """
        :type user_args: list
        :param user_args: list of gotten arguments
        :rtype: dict
        :return: dictionary of arguments
        """

        parser = argparse.ArgumentParser()
        for arg in self.get_unique_args(self.available_args):
            parser.add_argument(arg['key'], **arg['params'])
        return vars(parser.parse_known_args(user_args)[0])

    @staticmethod
    def get_unique_args(args):
        """
        :type: list
        :param args: list of parameters properties
        :rtype: list
        :return: return list of distinct parameters
        """
        sorted_args = sorted(args, key=lambda x: x['key'])
        return [list(group)[0] for key, group
                in groupby(sorted_args, lambda x: x['key'])]
