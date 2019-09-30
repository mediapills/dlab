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
# *****************************************************************************
from time import sleep
import unittest

from dlab_core.domain.exceptions import DLabException
from dlab_core.domain.helper import validate_property_type, break_after


class MockClass(object):
    def __init__(self, prop):
        self.prop = prop

    @property
    def prop(self):
        return self._prop

    @prop.setter
    @validate_property_type(str)
    def prop(self, val):
        self._prop = val


class TestHelper(unittest.TestCase):

    def test_valid_property_type(self):
        test_value = 'test'
        self.assertEqual(MockClass(test_value).prop, test_value)

    def test_invalid_property_type(self):
        test_values = [1, {}, (), None, []]
        for val in test_values:
            with self.assertRaises(DLabException):
                MockClass(val)

    def test_break_after_decorator(self):
        @break_after(3)
        def test_fn():
            sleep(10)

        with self.assertRaises(DLabException):
            test_fn()
