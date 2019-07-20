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

from dlab_core.infrastructure import dispatchers
from mock import MagicMock


class TestEventDispatcher(unittest.TestCase):

    def setUp(self):
        self.dispatcher = dispatchers.EventDispatcher()

    def test_add_non_callable_listener(self):
        with self.assertRaises(dispatchers.DispatcherExpectedCallableException):
            self.dispatcher.add_listener('param', 'text')

    def test_add_lambda_listener(self):
        self.dispatcher.add_listener('param', lambda: 'success')

        self.assertTrue(self.dispatcher.has_listeners('param'))

    def test_add_function_listener(self):
        def test():
            pass

        self.dispatcher.add_listener('param', test)

        self.assertTrue(self.dispatcher.has_listeners('param'))

    def test_add_class_method_listener(self):
        class Test:
            def func(self):
                pass

        obj = Test()
        self.dispatcher.add_listener('param', getattr(obj, 'func'))

        self.assertTrue(self.dispatcher.has_listeners('param'))

    def test_get_none_listeners(self):
        self.assertIsNone(self.dispatcher.get_listeners('param'))

    def test_get_wrong_listener(self):
        def func():
            pass

        self.dispatcher.add_listener('param', func)

        self.assertIsNotNone(self.dispatcher.get_listeners('param'))
        self.assertEqual(func, self.dispatcher.get_listeners('param')[0])

        self.assertIsNone(self.dispatcher.get_listeners('wrong'))

    def test_dispatch_other(self):
        self.dispatcher.add_listener(
            'param',
            lambda: (_ for _ in ()).throw(Exception)
        )

        self.assertIsNone(self.dispatcher.dispatch('other'))

    def test_dispatch_lambda(self):
        self.dispatcher.add_listener(
            'param',
            lambda: (_ for _ in ()).throw(Exception)
        )

        with self.assertRaises(Exception):
            self.dispatcher.dispatch('param')

    def test_dispatch_function(self):
        def test():
            raise Exception

        self.dispatcher.add_listener('param', test)

        with self.assertRaises(Exception):
            self.dispatcher.dispatch('param')

    def test_dispatch_object(self):
        obj = MagicMock()

        self.dispatcher.add_listener('param', getattr(obj, 'func'))

        self.dispatcher.dispatch('param')

        obj.func.assert_called()
