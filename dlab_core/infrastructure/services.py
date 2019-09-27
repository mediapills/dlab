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
from dlab_core.infrastructure.logger import StreamLogBuilder

from jose import jwt, JOSEError


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class KeyCloakError(Exception):
    pass


class ConnectionError(KeyCloakError):
    pass


class KeyCloak(object):
    """Client for KeyCloak interaction """

    def __init__(self, keycloak_server, realm_name, client_id, client_secret):
        self._realm_address = keycloak_server + 'realms/' + realm_name
        self._client_id = client_id
        self._client_secret = client_secret
        self.logger = StreamLogBuilder('keycloak', INFO).logging
        self._pub_key = self.get_key()

    def make_request_to_server(self, method='GET', endpoint='', **kwargs):
        """Performs request to KeyCloak server and checks response

        :type method: str
        :param method: method for the HTTP request
        :type endpoint: str
        :param endpoint: KeyCloak server endpoint to make request to

        :rtype: requests.Response
        :return: HTTP response object
        """
        endpoint = self._realm_address + endpoint
        kwargs['verify'] = True
        response = requests.request(method, endpoint, **kwargs)
        self.check_response(response)
        return response

    def check_response(self, response):
        """Checks response status code

        :type response: requests.Response
        :param response: :class:`Response <Response>` object

        :rtype: requests.Response
        :return: :class:`Response <Response>` object

        :raises InvalidResponseError: if response status code is not 200
        """
        if response.status_code > 200:
            raise ConnectionError('Server responded with {} - {}'.format(
                response.status_code, response.content.decode('utf8')
            ))

    def get_key(self):
        """Retrieves public key from KeyCloak realm

        :rtype: str
        :return: public key for token decoding
        """
        response = self.make_request_to_server()
        return response.json()['public_key']

    def validate_token(self, access_token):
        """Validates signature of given token and introspects it

        :type access_token: str
        :param access_token: JWT-token

        :rtype: bool
        :return: True if token is valid and active, False otherwise
        """
        sig_valid = self.validate_signature(access_token)
        is_active = self.introspect_token(access_token)
        return sig_valid and is_active

    def validate_signature(self, access_token):
        """Validates signature of given token

        :type access_token: str
        :param access_token: JWT-token

        :rtype: bool
        :return: True if token is valid, False otherwise
        """
        try:
            jwt.decode(access_token, key=self._pub_key)
            return True
        except JOSEError as e:
            self.logger.log(ERROR, str(e))
            return False

    def introspect_token(self, access_token):
        """Introspects given token

        :type access_token: str
        :param access_token: JWT-token

        :rtype: bool
        :return: True if token is active, False otherwise
        """
        response = self.make_request_to_server(
            method='POST',
            endpoint='/protocol/openid-connect/token/introspect',
            data={'token': access_token},
            auth=(self._client_id, self._client_secret)
        )
        return response.json().get('active')
