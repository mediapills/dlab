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
from dlab_core.domain.helper import break_after, validate_property_type


class TestHelper(unittest.TestCase):

    def test_break_after_decorator(self):
        @break_after(3)
        def test_fail():
            sleep(10)

        with self.assertRaises(DLabException):
            test_fail()

    def test_validate_property_type_index_error(self):
        @validate_property_type(str, 2)
        def test_index_error():
            pass

        with self.assertRaises(DLabException):
            test_index_error()

    def test_validate_property_type_error(self):
        @validate_property_type(str)
        def test_type_error(val):
            pass
        values = [1, {}, [], (), None]
        for v in values:
            with self.assertRaises(DLabException):
                test_type_error(v)
