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

from dlab.infrastructure.validators import JSONValidator


@six.add_metaclass(abc.ABCMeta)
class BaseValidatorTestCase:

    @abc.abstractmethod
    def test_invalid_json(self):
        pass

    @abc.abstractmethod
    def test_valid_json(self):
        pass


class TestJSONValidator(BaseValidatorTestCase, unittest.TestCase):
    TEST_SCHEMA = {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "status": {"type": "boolean"},
            "value_a": {"type": "number"}
        },
        "required": ["value_a", "status"],
        }

    def setUp(self):
        self.validator = JSONValidator(self.TEST_SCHEMA)

    def test_invalid_json(self):
        test_data = {"description": "Hello world", "status": True}

        valid = self.validator.validate(test_data)

        self.assertFalse(valid)

    def test_valid_json(self):
        test_data = {"description": "Hello world", "value_a": 111, "status": True}

        valid = self.validator.validate(test_data)

        self.assertTrue(valid)
