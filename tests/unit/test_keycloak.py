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

from dlab_core.domain.exceptions import DLabException
from dlab_core.infrastructure.services import (
    KeyCloak, KeyCloakConnectionException
)

from mock import patch

from requests.exceptions import RequestException

MOCK_PUBLIC_KEY = 'secret'
MOCK_VALID_TOKEN = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiWXVyYSJ9.bG1BjdKLzqdx1qho'
    'eg4B598nV9JOds0-23xgRXG-n5c'
)
MOCK_INVALID_TOKEN = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiWXVyYSJ9.bG1BjdKLzqdx1qho'
)


class MockResponse:
    def __init__(self, active=True, ok=True):
        self.json_data = {
            'public_key': MOCK_PUBLIC_KEY,
            'active': active
        }
        self.ok = ok

    def raise_for_status(self):
        if not self.ok:
            raise RequestException('Bad request')

    def json(self):
        return self.json_data


class TestKeyCloak(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestKeyCloak, self).__init__(*args, **kwargs)
        with patch('requests.request', return_value=MockResponse()):
            self.keycloak = KeyCloak(
                keycloak_host='https://test-ip.com/auth/',
                realm_name='test_realm',
                client_id='client',
                client_secret='secret'
            )
            self.keycloak._pub_key = 'secret'

    @patch('requests.request', return_value=MockResponse())
    def test_valid_token(self, *args):
        self.assertTrue(self.keycloak.validate_token(MOCK_VALID_TOKEN))

    @patch('requests.request', return_value=MockResponse())
    def test_invalid_token_signature(self, *args):
        self.assertFalse(self.keycloak.validate_token(MOCK_INVALID_TOKEN))

    @patch('requests.request', return_value=MockResponse(active=False))
    def test_inactive_token(self, *args):
        self.assertFalse(self.keycloak.validate_token(MOCK_VALID_TOKEN))

    @patch('requests.request', return_value=MockResponse(ok=False))
    def test_bad_server_request(self, *args):
        with self.assertRaises(KeyCloakConnectionException):
            self.keycloak.validate_token(MOCK_VALID_TOKEN)


class TestKeyCloakInvalidArgFormat(unittest.TestCase):

    def test_bad_argument_format(self):
        with self.assertRaises(DLabException):
            self.keycloak = KeyCloak(
                keycloak_host='https://test-ip.com/auth/',
                realm_name='test_realm',
                client_id='client',
                client_secret=5
            )
