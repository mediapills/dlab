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
from contextlib import contextmanager
import os
import subprocess

import paramiko
import six


@six.add_metaclass(abc.ABCMeta)
class BaseCommandExecutor(object):

    @abc.abstractmethod
    def run(self, command):
        """Run cli command
        :type command: str
        :param command: cli command
        """

        raise NotImplementedError

    @abc.abstractmethod
    def sudo(self, command):
        """Run cli sudo command
        :type command: str
        :param command: cli command
        """

        raise NotImplementedError

    @abc.abstractmethod
    def cd(self, path):
        """Change work directory to path
        :type path: str
        :param path: directory location
        """

        raise NotImplementedError


class LocalCommandExecutor(BaseCommandExecutor):

    def run(self, command):
        """Run cli command
        :type command: str
        :param command: cli command
        :rtype: str
        :return execution result
        """
        lines = []
        process = subprocess.Popen(
            command, shell=True, universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while process.poll() is None:
            line = process.stdout.readline()
            lines.append(line)
            # TODO: Add logging

        return ' '.join(lines)

    def sudo(self, command):
        """Run cli sudo command
        :type command: str
        :param command: cli command
        :rtype: str
        :return execution result
        """

        raise NotImplementedError

    @contextmanager
    def cd(self, path):
        """Change work directory to path
        :type path: str
        :param path: directory location
        """

        current_dir = os.getcwd()
        try:
            os.chdir(path)
            yield
        finally:
            os.chdir(current_dir)


class ParamikoCommandExecutor(BaseCommandExecutor):

    def __init__(self, host, name, identity_file):
        """
        :type host: str
        :param host: ip address or host name
        :type name: str
        :param name: user name
        :type: str
        :param identity_file: path to file
        """

        self.current_dir = None
        self._connection = None
        self.host = host
        self.name = name
        self.identity_file = identity_file

    @property
    def connection(self):
        if not self._connection:
            self._connection = paramiko.SSHClient()
            self._connection.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self._connection.connect(self.host, username=self.name,
                                     key_filename=self.identity_file)
        return self._connection

    @property
    def current_dir(self):
        return self._current_dir

    @current_dir.setter
    def current_dir(self, val):
        self._current_dir = val

    def run(self, command):
        """Run cli command
        :type command: str
        :param command: cli command
        :rtype: str
        :return execution result
        """

        if self.current_dir:
            command = 'cd {}; {}'.format(self.current_dir, command)
        stdin, stdout, stderr = self.connection.exec_command(command)
        return stdout.read().decode('ascii').strip("\n")

    def sudo(self, command):
        """Run sudo cli command
        :type command: str
        :param command: cli command
        :rtype: str
        :return execution result
         """
        command = 'sudo {}'.format(command)
        return self.run(command)

    @contextmanager
    def cd(self, path):
        try:
            self.current_dir = path
            yield
        finally:
            self.current_dir = None
