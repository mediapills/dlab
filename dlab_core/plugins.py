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

from dlab_core.domain.exceptions import DLabException
from dlab_core.registry import context, CONTAINER_PARAM_PLUGINS

LC_ERR_PLUGIN_LOADED = 'Plugin "{cls}" already loaded.'

LC_ERR_KEY_ALREADY_EXISTS = 'Plugin key "{name}" already exists.'


class PluginRegistryException(DLabException):
    pass


class PluginRegistryTypeException(PluginRegistryException):
    pass


class PluginRegistry:
    """Decorator for plugin registry. Register plugin loader after first
    bootstrap and avoid second execution.

    :type name: str
    :param name: Plugin name.
    """
    def __init__(self, name):
        self.name = name

    @staticmethod
    def validate(key, val):
        """
        :type key: str
        :param key: Plugin name.

        :type val: str
        :param val: Class name.

        :raises: PluginRegistryException if plugin or class is already exists
        """
        get_plugins = context.raw(CONTAINER_PARAM_PLUGINS)
        plugins = get_plugins(context)

        if key in plugins:
            raise PluginRegistryException(
                LC_ERR_KEY_ALREADY_EXISTS.format(name=key))

        if val in plugins.values():
            raise PluginRegistryException(
                LC_ERR_PLUGIN_LOADED.format(cls=val))

    def register(self, cls):
        """
        :type cls: class
        :param cls: Plugin class.
        """
        self.validate(self.name, cls.__name__)
        context.extend(
            CONTAINER_PARAM_PLUGINS,
            lambda p, c: dict(p, **{self.name: cls.__name__}))

    def __call__(self, cls):
        self.register(cls)
        return cls
