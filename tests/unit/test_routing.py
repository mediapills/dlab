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

from dlab_core.routing import (
    CLIRoute, RouteArgumentTypeException,
    RouteArgumentKeyException, RouteArgumentValueException,
    RouteInvokeCallableException, CLIRouter)

from mock import Mock


class TestRoute(unittest.TestCase):

    def setUp(self):
        self._mock = Mock()

    def test_arguments_validation(self):
        for i in [1, 'str', None, False, ['test'], ('test',), {'test'}]:
            with self.assertRaises(RouteArgumentTypeException):
                CLIRoute(self._mock.help, i)

    def test_invoke_validation(self):
        with self.assertRaises(RouteInvokeCallableException):
            CLIRoute(None, {0: 'test'})

    def test_arguments_key_validation(self):
        with self.assertRaises(RouteArgumentKeyException):
            CLIRoute(self._mock.help, {None: 'test'})

    def test_arguments_value_validation(self):
        with self.assertRaises(RouteArgumentValueException):
            CLIRoute(self._mock.help, {0: None})


class TestRouter(unittest.TestCase):

    def setUp(self):
        self._mock = Mock()
        self._router = CLIRouter()

    def test_empty_router(self):
        self.assertListEqual([], self._router.match([]))

    def test_match(self):
        self._router.add(CLIRoute(self._mock.help, {0: 'test', 2: 'route'}))
        for route in self._router.match(['test', 'dlab', 'route']):
            route.invoke()
        self._mock.help.assert_called()

    def test_priority_match(self):
        self._router.add(CLIRoute(self._mock.help, {0: 'test', 1: 'dlab'}))
        self._router.add(CLIRoute(self._mock.help2, {1: 'dlab', 2: 'route'}))
        self._router.add(CLIRoute(self._mock.help3, {0: 'test', 2: 'route'}))

        for route in self._router.match(['test', 'dlab', 'route']):
            route.invoke()

        self._mock.help2.assert_called()
        self._mock.help.assert_not_called()
        self._mock.help3.assert_not_called()

    def test_multiple_match(self):
        self._router.add(CLIRoute(self._mock.help, {0: 'test', 2: 'route'}))
        self._router.add(CLIRoute(self._mock.help2, {0: 'test', 2: 'route'}))

        for route in self._router.match(['test', 'dlab', 'route']):
            route.invoke()

        self._mock.help.assert_called()
        self._mock.help2.assert_called()
