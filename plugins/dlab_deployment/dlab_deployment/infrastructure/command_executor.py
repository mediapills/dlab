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
            # ToDo: Add logging

        return ' '.join(lines)

    def sudo(self, command):
        """Run cli sudo command
        :type command: str
        :param command: cli command
        :rtype: str
        :return execution result
        """

        command = 'sudo {}'.format(command)
        return self.run(command)

    @contextmanager
    def cd(self, path):
        """Change work directory to path
        :type path: str
        :param path: directory location
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            os.chdir(path)
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
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection = ssh.connect(
            host, username=name, key_filename=identity_file)

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
        return stdout

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
        finally:
            self.current_dir = None
