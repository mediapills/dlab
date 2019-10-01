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

from dlab_deployment.infrastructure import command_executor
from dlab_deployment.infrastructure.command_executor import (
    LocalCommandExecutor, ParamikoCommandExecutor)


class TestLocalCommandExecutor(unittest.TestCase):

    @patch('os.chdir')
    def test_cd(self, mock):
        executor = LocalCommandExecutor()
        with executor.cd('test'):
            pass
        self.assertEqual(mock.call_count, 2)

    @patch.object(command_executor, 'copyfile')
    def test_put(self, mock):
        executor = LocalCommandExecutor()
        executor.put('test', 'test2')
        mock.assert_called()


def mock_connection(fn):
    def wrapper(self, *args, **kwargs):
        with patch('paramiko.SSHClient', return_value=self.connect_mock):
            return fn(self, self.connect_mock, *args, **kwargs)

    return wrapper


class TestParamikoCommandExecutor(unittest.TestCase):
    def setUp(self):
        self.connect_mock = MagicMock()
        output_mock = MagicMock()
        output_mock.read.return_value = 'output'.encode('utf-8')
        self.connect_mock.exec_command.return_value = (
            'in', output_mock, 'err')
        self.executor = ParamikoCommandExecutor('host', 'name', 'key')

    @mock_connection
    def test_run(self, mock):
        self.executor.run('ls')
        mock.exec_command.assert_called_with('ls')

    @mock_connection
    def test_sudo(self, mock):
        self.executor.sudo('ls')
        mock.exec_command.assert_called_with('sudo ls')

    @mock_connection
    def test_cd_run(self, mock):
        with self.executor.cd('test'):
            self.executor.run('ls')
        mock.exec_command.assert_called_with('cd test; ls')

    @mock_connection
    def test_cd_sudo(self, mock):
        with self.executor.cd('test'):
            self.executor.sudo('ls')
        mock.exec_command.assert_called_with('cd test; sudo ls')

    @mock_connection
    def test_connection_init_error(self, mock):
        mock.connect = MagicMock(side_effect=[Exception, None])
        self.executor.run('ls')
        mock.exec_command.assert_called_with('ls')

    @patch.object(ParamikoCommandExecutor, 'current_dir',
                  new_callable=PropertyMock)
    def test_cd(self, current_dir_mock):
        with self.executor.cd('test'):
            pass
        self.assertEqual(current_dir_mock.call_count, 2)

    @patch.object(command_executor, 'SCPClient')
    def test_put(self, scp_client):
        with patch('paramiko.SSHClient'):
            self.executor.put('test', 'test')
            scp_client().put.assert_called()
