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
import random

from dlab_core.registry import (
    context, register_context, extend_context, freeze_context, load_plugins,
    add_hook, do_action, CONTAINER_PARAM_EVENT_DISPATCHER)
from mock import patch, MagicMock

dispatcher = context.raw(CONTAINER_PARAM_EVENT_DISPATCHER)


class TestFunctions(unittest.TestCase):

    def setUp(self):
        # TODO implementation needs to be done in ContextBuilder
        context.clear()
        context[CONTAINER_PARAM_EVENT_DISPATCHER] = dispatcher

    def test_register_context(self):
        register_context('param', lambda c: 'value')

        self.assertEqual('value', context['param'])

    def test_extend_context(self):
        register_context('param', lambda c: 'value')
        extend_context('param', lambda v, c: 'extended_' + v)

        self.assertEqual('extended_value', context['param'])

    def test_freeze_context(self):
        def test():
            return random.random()

        freeze_context('random', test)

        a = context['random']
        b = context['random']

        self.assertNotEqual(a(), b())

    def test_add_hook(self):
        name = 'init.param'
        add_hook(
            name, lambda: register_context('param', lambda c: 'value'))

        self.assertTrue(
            context[CONTAINER_PARAM_EVENT_DISPATCHER].has_listeners(name))

    def test_function_call(self):
        @do_action('hook_name')
        def test():
            pass

        func = MagicMock()
        add_hook('hook_name', func)

        func.assert_not_called()

        test()

        func.assert_called()

    def test_instance_method_call(self):
        class Test:
            @do_action('hook_name')
            def test(self):
                pass

        func = MagicMock()
        add_hook('hook_name', func)
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
        ep = bootstrap = MagicMock()
        ep.load = MagicMock(return_value=bootstrap)

        with patch(
                'pkg_resources.iter_entry_points',
                return_value=[ep]):
            load_plugins()

        bootstrap.assert_called()

    def test_load_plugin_exception(self):
        ep = bootstrap = MagicMock()
        ep.load = MagicMock(return_value=bootstrap)

        with patch.dict(sys.modules, {'pkg_resources': None}):
            load_plugins()

        bootstrap.assert_not_called()
