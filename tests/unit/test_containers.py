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

from dlab_core.containers import (
    ContainerFrozenServiceException, ContainerExpectedCallableException,
    ContainerTypeException, ContainerKeyException, Container)


def func_mock(c):
    return 'value'


class TestContainer(unittest.TestCase):

    def setUp(self):
        self.c = Container()

    def test_constructor(self):
        b = Container({'key': 'val'})

        self.assertEqual('val', b['key'])

    def test_constructor_error(self):
        with self.assertRaises(ContainerTypeException):
            Container('test')

    def test_string(self):
        self.c['param'] = 'value'

        self.assertEqual('value', self.c['param'])

    def test_closure(self):
        self.c['param'] = lambda c: 'value'

        self.assertEqual('value', self.c['param'])

    def test_closure_of_closure(self):
        self.c['param'] = lambda c: func_mock

        self.assertEqual(func_mock, self.c['param'])

    def test_object(self):
        obj = type("Foo", (object,), {})()

        self.c['param'] = obj

        self.assertEqual(obj, self.c['param'])

    def test_none(self):
        param = None
        self.c[param] = 'value'

        self.assertEqual('value', self.c[param])

    def test_unavailable(self):
        with self.assertRaises(ContainerKeyException):
            self.c['unavailable']

    def test_len(self):
        self.assertEqual(0, len(self.c))

        self.c['param'] = 'value'

        self.assertEqual(1, len(self.c))

    def test_delete(self):
        self.c['param'] = 'value'
        del self.c['param']

        self.assertFalse('param' in self.c.keys())

    def test_delete_unavailable(self):
        with self.assertRaises(ContainerKeyException):
            del self.c['param']

    def test_repr(self):
        self.assertIsInstance(repr(self.c), str)

    def test_clear(self):
        self.c['param'] = lambda c: 'value'
        self.c.clear()

        self.assertEqual(0, len(self.c.keys()))

    def test_iter(self):

        self.c['param1'] = 'value1'
        self.c['param2'] = 'value2'

        keys = set()
        vals = set()

        for i in self.c:
            keys.add(i)
            vals.add(self.c[i])

        self.assertEqual({'value1', 'value2'}, vals)
        self.assertEqual({'param1', 'param2'}, keys)

    def test_frozen_exception(self):
        self.c['param'] = lambda c: 'value'
        self.c['param']

        with self.assertRaises(ContainerFrozenServiceException):
            self.c['param'] = 'value'

    def test_frozen_delete(self):
        self.c['param'] = lambda c: 'value'
        a = self.c['param']

        self.assertEqual('value', a)

        del self.c['param']

        self.assertFalse('param' in self.c._frozen)

    def test_raw_data(self):
        self.c['param'] = func_mock

        self.assertEqual(func_mock, self.c.raw('param'))

    def test_raw_key_exception(self):
        with self.assertRaises(ContainerKeyException):
            self.c.raw('param')

    def test_raw_is_set(self):
        self.c['param'] = func_mock
        self.c['param']

        self.assertEqual(func_mock, self.c.raw('param'))

    def test_raw_delete(self):
        self.c['param'] = lambda c: 'value'
        self.c['param']

        self.assertTrue('param' in self.c._raw.keys())

        del self.c['param']

        self.assertFalse('param' in self.c._raw.keys())

    def test_non_callable_protected(self):
        with self.assertRaises(ContainerExpectedCallableException):
            self.c.protect('value')

    def test_callable_protected(self):
        self.assertEqual(func_mock, self.c.protect(func_mock))

        self.c['param'] = func_mock

        self.assertEqual(func_mock, self.c['param'])

    def test_delete_protected(self):
        self.c.protect(func_mock)
        self.assertTrue(func_mock in self.c._protected)

        self.c['param'] = func_mock
        del self.c['param']

        self.assertFalse(func_mock in self.c._protected)

    def test_extend(self):

        def func(message, c):
            return 'Extended ' + message

        self.c['param'] = func_mock

        self.c.extend('param', func)

        self.assertEqual('Extended value', self.c['param'])

    def test_extend_non_callable(self):
        self.c['param'] = func_mock

        with self.assertRaises(ContainerExpectedCallableException):
            self.c.extend('param', 'test')

    def test_extend_frozen(self):
        def func(message, c):
            return 'Extended ' + message

        self.c['param'] = lambda c: 'value'
        self.c['param']

        with self.assertRaises(ContainerFrozenServiceException):
            self.c.extend('param', func)
