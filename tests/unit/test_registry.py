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
import random

from dlab_core.registry import (
    register_context, extend_context, freeze_context, load_plugins,
    do_action, add_hook, get_resource, RegistryLoadException, reload_context,
    CONTAINER_PARAM_PLUGINS)

from mock import patch, MagicMock


class EntryPointMock(MagicMock):
    name = 'test'
    module_name = 'bootstrap'


class TestFunctions(unittest.TestCase):

    def setUp(self):
        reload_context()

    def test_register_context(self):
        register_context('param', lambda c: 'value')

        self.assertEqual('value', get_resource('param'))

    def test_extend_context(self):
        register_context('param', lambda c: 'value')
        extend_context('param', lambda v, c: 'extended_' + v)

        self.assertEqual('extended_value', get_resource('param'))

    def test_freeze_context(self):
        def test():
            return random.random()

        freeze_context('random', test)

        a = get_resource('random')
        b = get_resource('random')

        self.assertNotEqual(a(), b())

    def test_function_call(self):
        @do_action('action.name')
        def test():
            pass

        func = MagicMock()
        add_hook('action.name', func)

        func.assert_not_called()

        test()

        func.assert_called()

    def test_instance_method_call(self):
        class Test:
            @do_action('action.name')
            def test(self):
                pass

        func = MagicMock()
        add_hook('action.name', func)
        t = Test()

        func.assert_not_called()

        t.test()

        func.assert_called()

    def test_static_method_call(self):
        class Test:

            @staticmethod
            @do_action('hook_name')
            def test():
                pass

        func = MagicMock()
        add_hook('hook_name', func)

        func.assert_not_called()

        Test.test()

        func.assert_called()

    def test_load_plugins(self):
        bootstrap = MagicMock()
        ep = EntryPointMock(**{'load.return_value': bootstrap})

        with patch('pkg_resources.iter_entry_points', return_value=[ep]):
            load_plugins()

        bootstrap.assert_called()

    def test_load_plugin_type_error(self):
        ep = EntryPointMock(**{'load.return_value': None})

        with patch('pkg_resources.iter_entry_points', return_value=[ep]):
            with self.assertRaises(RegistryLoadException):
                load_plugins()

    def test_load_same_plugin_twice(self):
        ep = EntryPointMock(**{'load.return_value': lambda: None})

        with patch('pkg_resources.iter_entry_points', return_value=[ep]):
            load_plugins()

            with self.assertRaises(RuntimeError):
                load_plugins()

    def test_load_same_plugin_twice_exception(self):
        ep = EntryPointMock(**{'load.return_value': lambda: None})

        with patch('pkg_resources.iter_entry_points', return_value=[ep, ep]):
            with self.assertRaises(RegistryLoadException):
                load_plugins()

    def test_load_repo_plugins(self):
        load_plugins()
        plugins = get_resource(CONTAINER_PARAM_PLUGINS)

        self.assertIn('aws', plugins.keys())
        self.assertIn('azure', plugins.keys())
        self.assertIn('gcp', plugins.keys())
