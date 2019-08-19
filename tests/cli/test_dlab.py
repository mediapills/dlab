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

    def test_cmd_help(self):
        self.options = ['-h']
        out, err, exitcode = self.capture()
        self.assertEqual('usage: dlab deploy\n', out)
        self.assertEqual(0, exitcode)

    def test_cmd_err_usage(self):
        out, err, exitcode = self.capture()
        self.assertEqual('usage: dlab deploy\n', err)
        self.assertEqual(1, exitcode)


class TestDLabDeploy(BaseCLITest):

    def test_cmd_help(self):
        self.options = ['deploy', '-h']
        out, err, exitcode = self.capture()
        expected_output = 'usage: dlab deploy [\'aws\', \'gcp\', \'azure\']\n'
        self.assertEqual(expected_output, out)
        self.assertEqual(0, exitcode)

    def test_cmd_err_usage(self):
        self.options = ['deploy']
        out, err, exitcode = self.capture()
        expected_err = 'usage: dlab deploy [\'aws\', \'gcp\', \'azure\']\n'
        self.assertEqual(expected_err, err)
        self.assertEqual(1, exitcode)


class TestDLabDeployAWS(BaseCLITest):

    def test_cmd_help(self):
        self.options = ['deploy', 'aws', '-h']
        out, err, exitcode = self.capture()
        expected_output = 'usage: dlab deploy aws [\'endpoint\', \'k8s\']\n'
        self.assertEqual(expected_output, out)
        self.assertEqual(0, exitcode)

    def test_cmd_err_usage(self):
        self.options = ['deploy', 'aws', 'not_existed_target']
        out, err, exitcode = self.capture()
        expected_err = 'usage: dlab deploy aws [\'endpoint\', \'k8s\']\n'
        self.assertEqual(expected_err, err)
        self.assertEqual(1, exitcode)

    def test_correct_cmd(self):
        self.options = ['deploy', 'aws', 'k8s']
        out, err, exitcode = self.capture()
        self.assertEqual('Success\n', out)
        self.assertEqual('', err)
        self.assertEqual(0, exitcode)
