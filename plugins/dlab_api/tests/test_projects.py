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
from tests.base_test import BaseTestAPI


class TestCreateProjectAPI(BaseTestAPI):
    def test_create_valid_data(self):
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

        self.assertEqual(resp.json['code'], 1)

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

    def test_get_project_status(self):
        resp = self.client.get('/project/name/status')

        self.assertDictEqual(resp.json, {"status": "running", "error_message": "string"})

    def test_delete_project(self):
        resp = self.client.delete('/project/name')

        self.assertEqual(resp.status, '202 ACCEPTED')

    def test_put_project_wrong_action(self):
        resp = self.client.put('/project/name/test')

        self.assertEqual(resp.status, '400 BAD REQUEST')

    def test_put_project_correct_action(self):
        resp = self.client.put('/project/name/start')

        self.assertEqual(resp.status, '202 ACCEPTED')