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
import os
import sys
import unittest

from api.command_builder import CommandBuilder

ENTITY = {'resource': 'resource_name',
          'action': 'action_name',
          'request': '{"project_name": "project_name"}'}


class TestCommandBuilder(unittest.TestCase):

    def setUp(self):
        self.cb = CommandBuilder(**ENTITY)
        self.executable_path = self.cb._CommandBuilder__executable_path

    def test_set_up(self):
        attr = hasattr(self.cb, 'resource')
        self.assertTrue(attr)

    def test_get_executable_path(self):
        self.assertEqual(
            os.path.dirname(sys.executable),
            self.executable_path
        )

    def test_dlab_path(self):
        self.assertEqual(
            self.cb.dlab,
            os.path.join(self.executable_path, 'dlab')
        )

    def test_python_path(self):
        self.assertEqual(
            self.cb.python,
            os.path.join(self.executable_path, 'python')
        )

    def test_params(self):
        self.assertEqual('--project_name=project_name', self.cb.params)

    def test_build_cmd(self):
        self.assertEqual(
            self.cb.build_cmd(),
            ' '.join([self.cb.python, self.cb.dlab,
             self.cb.resource, self.cb.action, self.cb.params])
        )
