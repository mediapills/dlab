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
# ******************************************************************************
import os
import sqlite3
import unittest

from mock import patch

from api.managers import APIManager, DaemonManager
from api.command_builder import CommandBuilder
from dlab_core.infrastructure.repositories import (SQLiteRepository,
                                                   FIFOSQLiteQueueRepository)


class TestAPIManager(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        with patch('sqlite3.connect') as connect:
            connect.return_value = sqlite3.connect(':memory:')
            self.api_manager = APIManager(os.path.join(
                self.base_dir, '..', 'database'
            ))

    def tearDown(self):
        del self.api_manager

    def test_set_up_manager(self):
        self.assertIsInstance(self.api_manager.repo, SQLiteRepository)
        self.assertIsInstance(self.api_manager.queue, FIFOSQLiteQueueRepository)

    def test_create_record(self):
        record_id = self.api_manager.create_record('data', 'resource', 'action')
        self.assertGreater(record_id, 0)


class TestDaemonManager(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.return_value = {
            'request': '{"request":"request"}',
            'action': 'action',
            'resource': 'resource'
        }
        self.builder = CommandBuilder(**self.return_value)

        with patch('sqlite3.connect', autospec=True) as connect:
            connect.return_value = sqlite3.connect(':memory:')
            self.daemon_manager = DaemonManager(os.path.join(
                self.base_dir, '..', 'database'
            ), 0, 1)

    @patch('persistqueue.FIFOSQLiteQueue.get')
    def test_start_task(self, mock_get):
        mock_get.return_value = b'1'

        self.assertEqual(self.daemon_manager.start_task(), '1')

    @patch('persistqueue.FIFOSQLiteQueue.task_done')
    def test_finish_task(self, mock_task_done):
        mock_task_done.return_value = None

        self.assertIsNone(self.daemon_manager.finish_task('1'))

    def test_process_error(self):
        self.assertIsNone(self.daemon_manager.process_error('1', 'error'))

    @patch('dlab_core.infrastructure.repositories.SQLiteRepository.find_one')
    def test_get_execution_command(self, mock_find_one):

        mock_find_one.return_value = self.return_value
        command = self.daemon_manager.get_execution_command('1')

        self.assertEqual(
            command,
            self.builder.build_cmd()
        )

    # @patch('api.managers.DaemonManager.start_task', return_value='1')
    # @patch('api.managers.DaemonManager.get_execution_command')
    # def test_run(self, mock_execution_command, *args):
    #     mock_execution_command.return_value = self.builder.build_cmd()
    #     self.daemon_manager.run()
