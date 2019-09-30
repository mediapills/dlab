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


class TestAPI(BaseTestAPI):

    def test_health_check(self):
        resp = self.client.get('/')
        self.assertEqual(resp.data.decode(), 'It works')


class TestCreateNotebooksAPI(BaseTestAPI):

    def test_create_valid_data(self):
        resp = self.client.post(
            '/notebook',
            json={
                'notebook': {"type": "jupyter"}, 'cloudConfig': {"type": "jupyter"}
            }
        )

        self.assertEqual(resp.json['code'], 1)

    def test_create_invalid_valid_data(self):
        resp = self.client.post(
            '/notebook',
            json={'qwerty': {"jupyter": "jupyter"}}
        )

        self.assertEqual(resp.json['code'], 0)


class TestNotebooksAPI(BaseTestAPI):

    def test_get_notebook_status(self):
        resp = self.client.get('/notebook/project/name/status')

        self.assertDictEqual(resp.json, {"status": "running", "error_message": "string"})

    def test_delete_notebook(self):
        resp = self.client.delete('/notebook/project/name')

        self.assertEqual(resp.status, '202 ACCEPTED')

    def test_put_notebook_wrong_action(self):
        resp = self.client.put('/notebook/project/name/test')

        self.assertEqual(resp.status, '400 BAD REQUEST')

    def test_put_notebook_correct_action(self):
        resp = self.client.put('/notebook/project/name/start')

        self.assertEqual(resp.status, '202 ACCEPTED')


class TestNotebookProjectLibAPI(BaseTestAPI):

    def test_get_notebook_lib(self):
        resp = self.client.get('/notebook/project/name/lib')

        self.assertDictEqual(resp.json, {})

    def test_post_notebook_lib_valid_data(self):
        resp = self.client.post('/notebook/project/name/lib',
                                json=[{
                                    'group': "jupyter",
                                    'name': "jupyter",
                                    'version': "jupyter",
                                }]
                                )

        self.assertDictEqual(resp.json, {u'code': 1})

    def test_post_notebook_lib_in_valid_data(self):
        resp = self.client.post('/notebook/project/name/lib',
                                json=[{'group': "jupyter"}]
                                )

        self.assertEqual(resp.status, '400 BAD REQUEST')


class TestNotebookLibAPI(BaseTestAPI):

    def test_get_notebook_lib_by_valid_type(self):
        resp = self.client.get('/notebook/jupyter')

        self.assertDictEqual(resp.json, {})

    def test_get_notebook_lib_by_in_valid_type(self):
        resp = self.client.get('/notebook/test')

        self.assertEqual(resp.json['code'], 0)
