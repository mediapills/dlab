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

from mock import patch, MagicMock, PropertyMock

from dlab_deployment.infrastructure.command_executor import (
    LocalCommandExecutor, ParamikoCommandExecutor)

PARAMIKO_CLIENT_CONNECT = 'paramiko.SSHClient.connect'


class TestLocalCommandExecutor(unittest.TestCase):

    @patch('os.chdir')
    def test_cd(self, mock):
        executor = LocalCommandExecutor()
        with executor.cd('test'):
            pass
        self.assertEqual(mock.call_count, 2)


class TestParamikoCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.connect_mock = MagicMock()
        self.connect_mock.exec_command.return_value = ('in', 'out', 'err')
        self.executor = ParamikoCommandExecutor('host', 'name', 'key')

    @patch(PARAMIKO_CLIENT_CONNECT)
    def test_run(self, mock):
        mock.return_value = self.connect_mock
        self.executor.run('ls')
        self.connect_mock.exec_command.assert_called_with('ls')

    @patch(PARAMIKO_CLIENT_CONNECT)
    def test_sudo(self, mock):
        mock.return_value = self.connect_mock
        self.executor.sudo('ls')
        self.connect_mock.exec_command.assert_called_with('sudo ls')

    @patch(PARAMIKO_CLIENT_CONNECT)
    def test_cd_run(self, mock):
        mock.return_value = self.connect_mock
        with self.executor.cd('test'):
            self.executor.run('ls')
        self.connect_mock.exec_command.assert_called_with('cd test; ls')

    @patch(PARAMIKO_CLIENT_CONNECT)
    def test_cd_sudo(self, mock):
        mock.return_value = self.connect_mock
        with self.executor.cd('test'):
            self.executor.sudo('ls')
        self.connect_mock.exec_command.assert_called_with('cd test; sudo ls')

    @patch.object(ParamikoCommandExecutor, 'current_dir',
                  new_callable=PropertyMock)
    def test_cd(self, current_dir_mock):
        with self.executor.cd('test'):
            pass
        self.assertEqual(current_dir_mock.call_count, 2)
