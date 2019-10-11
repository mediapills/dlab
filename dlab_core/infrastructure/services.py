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

from dlab_core.domain.exceptions import DLabException
from dlab_core.domain.helper import validate_property_type

from jose import jwt


URL_INTROSPECT = '{realm_address}/protocol/openid-connect/token/introspect'


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class KeyCloakException(DLabException):
    pass


class KeyCloakConnectionException(KeyCloakException):
    pass


class KeyCloak(object):
    """Client for KeyCloak interaction

    :type keycloak_host: str
    :param keycloak_host: IP or hostname for KeyCloak server to use

    :type realm_name: str
    :param realm_name: name of the KeyCloak Realm to use

    :type client_id: str
    :param client_id: KeyCloak Client to use for token introspection

    :type client_secret: str
    :param client_secret: KeyCloak Client secret string
    """
    def __init__(self, keycloak_host, realm_name, client_id, client_secret):
        if not (isinstance(keycloak_host, str) and isinstance(realm_name, str)):
            raise DLabException(
                'Either Keycloak host or Realm name '
                'has invalid type ({}, {})'.format(keycloak_host, realm_name)
            )
        self.realm_address = (keycloak_host, realm_name)
        self.client_id = client_id
        self.client_secret = client_secret
        self._pub_key = None

    @property
    def realm_address(self):
        return self._realm_address

    @realm_address.setter
    def realm_address(self, value):
        self._realm_address = '{}/realms/{}'.format(
            value[0].rstrip('/'), value[1]
        )

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    @validate_property_type(str)
    def client_id(self, value):
        self._client_id = value

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    @validate_property_type(str)
    def client_secret(self, value):
        self._client_secret = value

    @property
    def public_key(self):
        if not self._pub_key:
            self._pub_key = self.retrieve_key()

        return self._pub_key

    def make_request_to_server(self, method='GET', endpoint='', verify=False,
                               **kwargs):
        """Performs request to endpoint

        :type method: str
        :param method: method for the HTTP request
        :type endpoint: str
        :param endpoint: endpoint to make request to
        :type verify: bool
        :param verify: whether to verify server's TLS certificate

        :rtype: requests.Response
        :return: HTTP response object
        """
        try:
            response = requests.request(
                method, endpoint, verify=verify, **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise KeyCloakConnectionException(str(e))

    def retrieve_key(self):
        """Retrieves public key from KeyCloak realm

        :rtype: str
        :return: public key for token decoding
        """
        response = self.make_request_to_server(endpoint=self.realm_address)
        if response:
            # PyJWT expects key to be in PEM format (including header/footer)
            return (
                '-----BEGIN PUBLIC KEY-----\n{}'
                '\n-----END PUBLIC KEY-----'
            ).format(response.json().get('public_key'))

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
            jwt.decode(access_token, key=self.public_key)
        except Exception:
            return False
        else:
            return True

    def introspect_token(self, access_token):
        """Introspects given token

        :type access_token: str
        :param access_token: JWT-token

        :rtype: bool
        :return: True if token is active, False otherwise
        """
        endpoint = URL_INTROSPECT.format(realm_address=self.realm_address)
        response = self.make_request_to_server(
            method='POST',
            endpoint=endpoint,
            data={'token': access_token},
            auth=(self.client_id, self.client_secret)
        )
        return response.json().get('active') if response else False
