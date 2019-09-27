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
import unittest

from mock import patch

from dlab_core.infrastructure.services import KeyCloak

MOCK_KEYS_DATA = {'public_key': 'secret'}
MOCK_VALID_TOKEN = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiWXVyYSJ9.bG1BjdKLzqdx1qho'
    'eg4B598nV9JOds0-23xgRXG-n5c'
)
MOCK_INVALID_TOKEN = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiWXVyYSJ9.bG1BjdKLzqdx1qho'
)


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.content = 'Unauthorized'.encode('utf8')

    def json(self):
        return self.json_data


class TestKeyCloak(unittest.TestCase):

    @patch('requests.get', return_value=MockResponse(MOCK_KEYS_DATA))
    def setUp(self, *args):
        self.keycloak = KeyCloak('client', 'secret')
        self.keycloak._pub_key = 'secret'

    @patch('requests.post', return_value=MockResponse({'active': True}))
    def test_valid_token(self, *args):
        self.assertTrue(self.keycloak.validate_token(MOCK_VALID_TOKEN))

    @patch('requests.post', return_value=MockResponse({'active': True}))
    def test_invalid_token_signature(self, *args):
        self.assertFalse(self.keycloak.validate_token(MOCK_INVALID_TOKEN))

    @patch('requests.post', return_value=MockResponse({'active': False}))
    def test_inactive_token(self, *args):
        self.assertFalse(self.keycloak.validate_token(MOCK_VALID_TOKEN))

    @patch('requests.post', return_value=MockResponse({}, 405))
    def test_bad_server_request(self, *args):
        self.assertFalse(self.keycloak.validate_token(MOCK_VALID_TOKEN))
