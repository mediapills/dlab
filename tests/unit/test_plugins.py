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
import unittest

from dlab_core.plugins import PluginRegistry, PluginRegistryException
from dlab_core.registry import context, CONTAINER_PARAM_PLUGINS


class TestRegistry(unittest.TestCase):

    def setUp(self):
        context.clear()
        context[CONTAINER_PARAM_PLUGINS] = lambda c: {}

    def test_register_class(self):
        @PluginRegistry('test')
        class TestClass:
            pass

        self.assertEqual(
            {'test': 'TestClass'},
            context[CONTAINER_PARAM_PLUGINS])

    def test_register_identical(self):
        @PluginRegistry('test')
        class TestClassOne:
            pass

        with self.assertRaises(PluginRegistryException):
            @PluginRegistry('test')
            class TestClassTwo:
                pass

    def test_register_same(self):
        with self.assertRaises(PluginRegistryException):
            @PluginRegistry('test_two')
            @PluginRegistry('test_one')
            class TestClass:
                pass

    def test_register_superclass(self):
        @six.add_metaclass(abc.ABCMeta)
        class SuperClass:
            def initialize(self):
                pass

        @PluginRegistry('test')
        class TestClass(SuperClass):
            pass

        self.assertEqual(
            {'test': 'TestClass'},
            context[CONTAINER_PARAM_PLUGINS])
