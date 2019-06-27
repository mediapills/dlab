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
import abc
import six
import sys
import unittest
import logging
from mock import patch, mock_open

from dlab_core.setup import AbstractParametersBuilder, AbstractDirector


def mock_file_content(content):
    """
    Mock file content

    :param content: str File content
    :return: Any
    """

    def decorator(func):

        def wrapper(*args):
            with patch('dlab_core.setup.open', mock_open(read_data=content)):
                return func(*args)

        return wrapper

    return decorator


def mock_file_content_not_found(func):
    """
    Mock side effect while open file

    :param func: function
    :return: Any
    """

    def wrapper(*args):
        with patch('dlab_core.setup.open') as _file:
            _file.side_effect = IOError('No such file or directory')
            return func(*args)

    return wrapper


def mock_packages(packages):
    """
    Mock packages

    :param packages: list packages
    :return: Any
    """

    def decorator(func):

        def wrapper(*args):
            with patch('dlab_core.setup.find_packages') as p:
                p.return_value = packages
                return func(*args)

        return wrapper

    return decorator


def mock_version(content):
    """
    Mock version

    :param content: version content
    :return: Any
    """

    def decorator(func):

        def wrapper(*args):
            with patch('dlab_core.setup.open', mock_open(read_data=content)):
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


@six.add_metaclass(abc.ABCMeta)
class BaseTestCase:
    REQUIREMENTS_FILE_CONTENT = 'flask\nsix'
    REQUIREMENTS_LIST = ['flask', 'six']
    REQUIREMENTS_LIST_WINDOWS = ['flask', 'six', 'pypiwin32']

    README_FILE_CONTENT = 'Long description...'

    PACKAGES = ['test_package']
    VERSION = '__version_info__ = \'0.0.0\''


class TestConcreteBuilder(BaseTestCase, unittest.TestCase):

    def setUp(self):
        self._builder = ConcreteBuilder()
        self.requirements = self.REQUIREMENTS_LIST_WINDOWS if \
            sys.platform == 'win32' else self.REQUIREMENTS_LIST

    @mock_file_content(BaseTestCase.REQUIREMENTS_FILE_CONTENT)
    def test_set_requirements(self):
        self._builder.set_requirements()
        params = self._builder.parameters['requirements']

        self.assertEqual(params, self.requirements)

    @mock_file_content(BaseTestCase.README_FILE_CONTENT)
    def test_set_long_description(self):
        self._builder.set_long_description()
        params = self._builder.parameters['long_description']

        self.assertEqual(params, self.README_FILE_CONTENT)

    @mock_packages(BaseTestCase.PACKAGES)
    def test_set_packages(self):
        self._builder.set_packages()
        params = self._builder.parameters['packages']

        self.assertEqual(params, self.PACKAGES)

    # TODO: Think how to get __version__ property during the test
    # @mock_version(BaseTestCase.VERSION)
    # def test_set_version(self):
    #     self._builder.set_version()

    def test_set_entry_points(self):
        self._builder.set_entry_points()

        self.assertEqual(self._builder.parameters['entry_points'], {})

    @mock_file_content_not_found
    def test_file_not_found_requirements(self):
        with self.assertRaises(IOError):
            self._builder.set_requirements()

    @mock_file_content_not_found
    def test_file_not_found_readme(self):
        with self.assertRaises(IOError):
            self._builder.set_long_description()

    # @mock_file_content_not_found
    # def test_file_not_found_version(self):
    #     with self.assertRaises(IOError):
    #         self._builder.set_version()


class TestConcreteDirector(BaseTestCase, unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        logger = logging.getLogger(__name__)
        self._builder = ConcreteBuilder()
        self._director = ConcreteDirector(logger)

    # @mock_file_content(BaseTestCase.REQUIREMENTS_FILE_CONTENT)
    # @mock_file_content(BaseTestCase.README_FILE_CONTENT)
    @mock_packages(BaseTestCase.PACKAGES)
    def test_director(self):
        self._director.build(self._builder)
        params = self._director.parameters

        self.assertTrue(True)


# create test with all keys
# create test with files availability
# create test Exception handling
