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
import sys

import six
import subprocess
import unittest


@six.add_metaclass(abc.ABCMeta)
class BaseCLITest(unittest.TestCase):
    def __init__(self, *args):
        self._cmd = None
        self._process = None
        self._options = []

        super(BaseCLITest, self).__init__(*args)

    @property
    def cmd(self):
        return 'dlab'

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def execute(self):
        if self._process is None:
            command = [self.cmd]
            command.extend(self.options)

            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

    @property
    def process(self):
        if self._process is None:
            self.execute()

        return self._process

    def capture(self):
        process = self.process
        out, err = process.communicate()
        return out, err, process.returncode

    def setUp(self):
        self.options = []


class TestDLab(BaseCLITest):

    # TODO check if sys.platform can help here for win
    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
    def test_cmd_help(self):
        out, err, exitcode = self.capture()
        self.assertEqual('', err)
        self.assertEqual(0, exitcode)
