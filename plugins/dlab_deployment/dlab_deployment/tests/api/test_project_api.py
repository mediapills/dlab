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
import sqlite3
import unittest

from mock import patch

from api.app import app
from dlab_core.infrastructure.repositories import STATUSES, DONE


class BaseTestAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()


class TestCreateProjectAPI(BaseTestAPI):

    @patch('sqlite3.connect', autospec=True)
    def test_create_valid_data(self, connect):
        connect.return_value = sqlite3.connect(':memory:')

        resp = self.client.post(
            '/project',
            json={
                "project": {
                    "useSharedImages": True,
                },
                "cloudProperties": {
                    "os": "string",
                }
            }
        )

        self.assertGreaterEqual(resp.json['code'], 1)

    def test_create_invalid_valid_data(self):
        resp = self.client.post(
            '/project',
            json={
                "project": {
                    "useSharedImages": True,
                }
            }
        )

        self.assertEqual(resp.json['code'], 0)


class TestProjectAPI(BaseTestAPI):

    @patch('sqlite3.connect', autospec=True)
    @patch('api.managers.APIManager.get_record')
    def test_get_project_status(self, mock_get_record, connect):
        connect.return_value = sqlite3.connect(':memory:')
        mock_get_record.return_value = {
            'request': '{"request":"request"}',
            'action': 'action',
            'resource': 'resource',
            'status': int(STATUSES[DONE])
        }

        resp = self.client.get('/project/1/status')

        self.assertDictEqual(resp.json,
                             {'code': 1, 'status': 'DONE'}
                             )

    @patch('sqlite3.connect', autospec=True)
    @patch('api.managers.APIManager.get_record')
    def test_get_project_status_wrong_value(self, mock_get_record, connect):
        connect.return_value = sqlite3.connect(':memory:')
        mock_get_record.return_value = {}

        resp = self.client.get('/project/2/status')

        self.assertDictEqual(resp.json,
                             {'code': 0, 'message': 'Project not found'}
                             )

    def test_delete_project(self):
        resp = self.client.delete('/project/name')

        self.assertEqual(resp.status, '202 ACCEPTED')

    def test_put_project_wrong_action(self):
        resp = self.client.put('/project/name/test')

        self.assertEqual(resp.status, '400 BAD REQUEST')

    def test_put_project_correct_action(self):
        resp = self.client.put('/project/name/start')

        self.assertEqual(resp.status, '202 ACCEPTED')
