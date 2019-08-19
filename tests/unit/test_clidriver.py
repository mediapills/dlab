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

from dlab_core.domain.exceptions import DLabException
from dlab_core.clidriver import BaseCliHandler
from mock import patch


class TestCLIDriver(unittest.TestCase):

    def test_keyboard_interrupt(self):
        with patch.object(
                BaseCliHandler, 'parse_args', side_effect=KeyboardInterrupt):
            self.assertEqual(130, BaseCliHandler().execute())

    def test_dlab_exception(self):
        with patch.object(
                BaseCliHandler, 'parse_args', side_effect=DLabException):
            self.assertEqual(255, BaseCliHandler().execute())

    def test_exception(self):
        with patch.object(
                BaseCliHandler, 'parse_args', side_effect=Exception):
            self.assertEqual(255, BaseCliHandler().execute())
