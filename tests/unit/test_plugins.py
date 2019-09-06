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

from mock import MagicMock, patch

from dlab_core.plugins import BasePlugin, PluginLoadException, BaseCLIPlugin

MOCK_PLUGINS_GROUP = 'test.group'
ENTRY_POINT_NAME = 'test'


class EntryPointMock(MagicMock):
    name = ENTRY_POINT_NAME
    module_name = 'bootstrap'


class TestPlugins(unittest.TestCase):
    def setUp(self):
        BasePlugin.clear_plugins()
        self._plugin_class = type(
            'Test', (BaseCLIPlugin,), {'base_routes': lambda: []})

    def test_load_plugins(self):
        ep = EntryPointMock(**{'load.return_value': self._plugin_class})

        with patch('pkg_resources.iter_entry_points', return_value=[ep]):
            for plugin in BasePlugin.load_plugins(MOCK_PLUGINS_GROUP):
                self.assertIsInstance(plugin, self._plugin_class)

    def test_load_plugin_type_error(self):
        mock = MagicMock()
        ep = EntryPointMock(**{'load.return_value': mock})

        with patch('pkg_resources.iter_entry_points', return_value=[ep]):
            with self.assertRaises(PluginLoadException):
                BasePlugin.load_plugins(MOCK_PLUGINS_GROUP)

    def test_load_same_plugin_twice_exception(self):
        ep = EntryPointMock(**{'load.return_value': self._plugin_class})

        with patch('pkg_resources.iter_entry_points', return_value=[ep, ep]):
            with self.assertRaises(PluginLoadException):
                BasePlugin.load_plugins(MOCK_PLUGINS_GROUP)

    def test_ep_routes(self):
        self.assertListEqual([], self._plugin_class().ep_routes)
