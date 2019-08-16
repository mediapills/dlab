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

import sys
import unittest

from dlab_core.setup import (
    SetupParametersDirector, SetupParametersBuilder, FileNotFoundException,
    SetupException)
from errno import ENOENT
from mock import patch, mock_open, Mock


LIB_NAME = 'dlab_core.setup.'

FN_OPEN = LIB_NAME + 'open'
FN_FIND_PACKAGES = LIB_NAME + 'find_packages'
FN_ISFILE = LIB_NAME + 'os.path.isfile'

MOCK_NAME = 'dlab_core'
MOCK_DESCRIPTION_SHORT = 'Test short description ...'

REQUIRED_FIELDS = {
    'version',
    'description',
    'author',
    'author_email',
    'url',
    'packages'}


def mock_isfile(result=True):

    def decorator(func):

        def wrapper(*args):
            with patch(FN_ISFILE, return_value=result):
                return func(*args)

        return wrapper

    return decorator


class TestSetupParametersBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = SetupParametersBuilder(
            MOCK_NAME,
            MOCK_DESCRIPTION_SHORT
        )

    def test_constructor(self):
        params = self.builder.parameters

        self.assertEqual(params['name'], MOCK_NAME)
        self.assertEqual(params['description'], MOCK_DESCRIPTION_SHORT)

    @patch(FN_FIND_PACKAGES, Mock(return_value=['foo', 'bar', 'baz']))
    def test_set_packages(self):
        self.builder.set_packages()
        params = self.builder.parameters

        self.assertEqual(params['packages'], ['foo', 'bar', 'baz'])

    @mock_isfile()
    @patch(FN_OPEN, mock_open(read_data="foo==1.0.0\nbar>=0.0.0\nbaz"))
    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
    def test_set_requirements(self):
        self.builder.set_requirements()
        params = self.builder.parameters

        self.assertEqual(params['install_requires'], [
            'foo==1.0.0',
            'bar>=0.0.0',
            'baz'
        ])

    @mock_isfile(False)
    def test_no_requirements_file(self):
        with self.assertRaises(FileNotFoundException):
            self.builder.set_requirements()

    @mock_isfile()
    @patch(FN_OPEN, mock_open(read_data=''))
    def test_set_requirements_for_win(self):
        with patch(LIB_NAME + 'sys') as mock:
            mock.platform = 'win32'

            self.builder.set_requirements()
            requires = self.builder.parameters['install_requires']

            self.assertGreater(len(requires), 0)

    @mock_isfile()
    @patch(FN_OPEN, mock_open(read_data='__version__ = "0.0.1"'))
    def test_set_lib_version(self):
        with patch(LIB_NAME + 'os.path') as mock:
            mock.isfile = lambda path: path == self.builder.lib_file

            self.builder.set_version()
            params = self.builder.parameters

            self.assertEqual(params['version'], '0.0.1')

    @patch(FN_OPEN, mock_open(read_data='__version__ = "0.0.1"'))
    def test_set_file_version(self):
        with patch(LIB_NAME + 'os.path') as mock:
            mock.isfile = lambda path: path == self.builder.version_file

            self.builder.set_version()
            params = self.builder.parameters

            self.assertEqual(params['version'], '0.0.1')

    @mock_isfile(False)
    def test_no_version_file(self):
        with self.assertRaises(SetupException):
            self.builder.set_version()

    @mock_isfile()
    @patch(FN_OPEN, Mock(side_effect=IOError(
        ENOENT,
        "No such file or directory",
        'some_file.txt'
    )))
    def test_version_file_read_error(self):
        with self.assertRaises(SetupException):
            self.builder.set_version()

    @mock_isfile()
    @patch(FN_OPEN, mock_open(read_data=''))
    def test_no_version_var(self):
        with self.assertRaises(SetupException):
            self.builder.set_version()

    @patch(FN_OPEN, mock_open(read_data='file content'))
    @mock_isfile()
    def test_version_not_exec_content(self):
        with self.assertRaises(SetupException):
            self.builder.set_version()

    @patch(FN_OPEN, mock_open(read_data='Long description ...'))
    @mock_isfile()
    def test_set_long_description(self):
        self.builder.set_long_description()
        params = self.builder.parameters

        self.assertEqual(params['long_description'], 'Long description ...')

    @mock_isfile(False)
    def test_no_long_description_file(self):
        with self.assertRaises(FileNotFoundException):
            self.builder.set_long_description()

    def test_all_required_exists(self):
        params = self.builder.parameters

        self.assertTrue(REQUIRED_FIELDS.issubset(params.keys()))

    # @mock_isfile()
    # @patch(FN_OPEN, mock_open(read_data='__version__ = "0.0.1"'))
    def test_entry_points(self):

        entry_point = {
            'dlab.plugin': [
                "custom = dlab_test.registry:bootstrap",
            ],
        }

        class CustomClass(SetupParametersBuilder):
            def entry_points(self):
                return entry_point

        builder = CustomClass(
            MOCK_NAME,
            MOCK_DESCRIPTION_SHORT
        )

        builder.set_entry_points()

        entry_points = builder.parameters['entry_points']

        self.assertEqual(entry_point, entry_points())


class TestSetupParametersDirector(unittest.TestCase):

    def test_all_required_exists(self):
        builder = SetupParametersBuilder(
            MOCK_NAME,
            MOCK_DESCRIPTION_SHORT
        )

        director = SetupParametersDirector()
        director.build(builder)

        params = director.parameters

        self.assertTrue(REQUIRED_FIELDS.issubset(params.keys()))
