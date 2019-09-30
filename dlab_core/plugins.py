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
import inspect
import sys

import pkg_resources
import six

from dlab_core.cli import show_help
from dlab_core.domain.exceptions import DLabException
from dlab_core.routing import CLIRoute

"""cli entry_points group name for plugins in setup.py"""
CLI_ENTRY_POINTS_GROUP_NAME = 'dlab.plugin.cli'
API_ENTRY_POINTS_GROUP_NAME = 'dlab.plugin.api'


class PluginLoadException(DLabException):
    pass


@six.add_metaclass(abc.ABCMeta)
class BasePlugin(object):
    _plugins = {}

    @classmethod
    def load_plugins(cls, group):
        """ Load external plugins."""
        plugins = []
        for ep in pkg_resources.iter_entry_points(group=group):
            key = '.'.join([group, ep.name])
            val = cls.load_entry_point(ep)
            if key in cls._plugins:
                raise PluginLoadException
            cls._plugins[key] = val
            plugins.append(val)
        return plugins

    @classmethod
    def clear_plugins(cls):
        """ Clear plugins."""
        cls._plugins = {}

    @classmethod
    def load_entry_point(cls, ep):
        """ Load EntryPoint

        :type ep: EntryPoint
        :param ep: Setup EntryPoint.

        :raises PluginLoadException:
        """
        plugin = ep.load()

        if not (inspect.isclass(plugin)
                and any([issubclass(plugin, base) for base in cls.__bases__])
                and plugin is not cls):
            raise PluginLoadException()

        return plugin()


@six.add_metaclass(abc.ABCMeta)
class BaseCLIPlugin(BasePlugin):

    @property
    def routes(self):
        return self.base_routes + self.ep_routes

    @property
    @abc.abstractmethod
    def base_routes(self):
        raise NotImplementedError

    @property
    def ep_group(self):
        return None

    @property
    def ep_routes(self):
        routes = []
        if self.ep_group:
            for plugin in self.load_plugins(self.ep_group):
                routes.extend(plugin.routes)
        return routes


@six.add_metaclass(abc.ABCMeta)
class BaseAPIPlugin(BasePlugin):
    ep_group = API_ENTRY_POINTS_GROUP_NAME
    # @property
    # def ep_group(self):
    #     return

    @staticmethod
    def add_routes(app):
        return app


class APIPlugin(BaseAPIPlugin):

    @classmethod
    def routes(cls, app):
        if cls.ep_group:
            for plugin in cls.load_plugins(cls.ep_group):
                plugin.add_routes(app)
        return app


class CLIPlugin(BaseCLIPlugin):
    @property
    def ep_group(self):
        return CLI_ENTRY_POINTS_GROUP_NAME

    @property
    def base_routes(self):
        route = CLIRoute(show_help, {0: sys.argv[0]})
        return [route]
