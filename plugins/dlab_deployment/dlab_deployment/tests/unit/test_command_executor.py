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
import os
import random
import string
import unittest

from mock import patch, PropertyMock, MagicMock

from dlab_deployment.infrastructure.command_executor import (
    LocalCommandExecutor, ParamikoCommandExecutor)

COMMAND = 'ls'


class TestLocalCommandExecutor(unittest.TestCase):
    def test_run(self):
        executor = LocalCommandExecutor()
        dir_content = executor.run(COMMAND)
        for file in os.listdir():
            self.assertIn(file, dir_content)

    def test_cd(self):
        executor = LocalCommandExecutor()
        cd_dir = ''.join(random.choice(string.ascii_letters) for _ in range(7))
        executor.run('mkdir {}'.format(cd_dir))
        cwd = os.getcwd()
        with executor.cd(cd_dir):
            self.assertEqual(os.getcwd(), os.path.join(cwd, cd_dir))
        self.assertEqual(os.getcwd(), cwd)
        executor.run('rm -r {}'.format(cd_dir))


#
class TestParamikoCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.connection_mock = MagicMock()
        self.connection_mock.exec_command.return_value = ('in', 'out', 'err')
        self.connection = patch.object(
            ParamikoCommandExecutor, 'connection', new_callable=PropertyMock,
            return_value=self.connection_mock)
        self.current_dir = patch.object(
            ParamikoCommandExecutor, 'current_dir', new_callable=PropertyMock,
            return_value=None)
        with patch.object(
                ParamikoCommandExecutor, '__init__', return_value=None):
            self.executor = ParamikoCommandExecutor()

    def test_run(self):
        with self.connection, self.current_dir:
            self.executor.run(COMMAND)
            self.connection_mock.exec_command.assert_called_with(COMMAND)

    def test_sudo(self):
        with self.connection, self.current_dir:
            self.executor.sudo(COMMAND)
            self.connection_mock.exec_command.assert_called_with(
                'sudo {}'.format(COMMAND))

    def test_cd(self):
        with self.connection:
            cd_dir = 'test'
            with self.executor.cd(cd_dir):
                self.executor.run(COMMAND)
                self.connection_mock.exec_command.assert_called_with(
                    'cd {}; {}'.format(cd_dir, COMMAND))
