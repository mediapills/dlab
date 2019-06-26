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

import io
import os
import six
import unittest
import logging
from mock import patch, mock_open

from dlab_core.setup import AbstractParametersBuilder, AbstractDirector
from dlab_core.setup import README_FILE, REQUIREMENTS_FILE


def mock_file_content(filename, content):
    """
    Mock file content

    :param filename: str File location
    :param content: str File content
    :return: Any
    """

    def decorator(func):

        def wrapper(*args):
            # TODO remove PyUnresolvedReferences after python 3 migration
            target = "builtin.open" if not six.PY2 else "__builtin__.open"

            # try:
            #     import unittest.mock as mock
            # except (ImportError,) as e:
            #     import mock

            target = 'dlab_core.setup.open'.format(__name__)

            with patch(target, new=mock_open(read_data='DDDD')) as _file:
                actual = AbstractParametersBuilder._get_file_content(filename)
                _file.assert_called_once_with(filename, 'r')


            # with patch('%s.open' % target, mock_open(read_data='test')):
            #     with open('/dev/null') as f:
            #         print(f.read())


            # with patch(target, new_callable=MockOpen) as open_mock:
            #     open_mock.default_behavior = DEFAULTS_MOCK
            #     open_mock.set_read_data_for('/tmp/f1', 'QWERTY')


            # with patch(target, mock_open(read_data=content)) as mock_file:
            #     assert open(filename).read() == content
            #     mock_file.assert_called_with(filename)

            return func(*args)

        return wrapper

    return decorator


class ConcreteDirector(AbstractDirector):
    pass


class ConcreteBuilder(AbstractParametersBuilder):
    @property
    def name(self):
        return 'dlab_test'

    @property
    def description(self):
        return 'description goes here'


class TestArrayRepository(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        logger = logging.getLogger(__name__)
        self._builder = ConcreteBuilder()
        self._director = ConcreteDirector(logger)

    # @mock_file_content(REQUIREMENTS_FILE, 'pytest,mock')
    @mock_file_content(README_FILE, 'Long description goes here ...')
    def test_director(self):
        self._director.build(self._builder)
        params = self._director.parameters

        self.assertTrue(True)


# create test with all keys
# create test with files availability
# create test Exception handling
