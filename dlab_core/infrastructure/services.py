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
import requests
import urllib3

from dlab_core.domain.logger import INFO, ERROR
from dlab_core.infrastructure import logger

from jose import jwt, JOSEError


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class KeyCloak(object):

    realm_address = 'https://52.11.45.11/auth/realms/dlab/'

    def __init__(self, client_id, client_secret):
        self.logger = self.set_up_logger()
        self._pub_key = self.get_key()
        self._client_id = client_id
        self._client_secret = client_secret

    def set_up_logger(self):
        keycloak_logger = logger.StreamLogging('keycloak')
        keycloak_logger.level = INFO
        return keycloak_logger

    def get_key(self):
        keys_json = requests.get(self.realm_address, verify=False).json()
        return self.build_key(keys_json['public_key'])

    def build_key(self, key):
        pub_pattern = '-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----'
        return pub_pattern.format(key)

    def validate_token(self, access_token):
        sig_valid = self.validate_signature(access_token)
        is_active = self.validate_token_is_active(access_token)
        return sig_valid and is_active

    def validate_signature(self, access_token):
        try:
            decoded_token = jwt.decode(access_token, key=self._pub_key)
            self.logger.log(INFO, 'Decoded token: {}'.format(decoded_token))
            return True
        except JOSEError as e:
            self.logger.log(ERROR, str(e))
            return False

    def validate_token_is_active(self, access_token):
        response = requests.post(
            self.realm_address + 'protocol/openid-connect/token/introspect',
            data={'token': access_token},
            auth=(self._client_id, self._client_secret),
            verify=False
        )
        if response.status_code > 200:
            self.logger.log(ERROR, 'Server responded with {} - {}'.format(
                response.status_code, response.content.decode('utf8')
            ))
            return False

        return response.json().get('active')
