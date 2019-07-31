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

import pkg_resources

from dlab_core.containers import Container
from dlab_core.domain.exceptions import DLabException
from dlab_core.dispatchers import EventDispatcher


__all__ = ['add_hook', 'do_action', 'load_plugins', 'load_context',
           'reload_context', 'extend_context', 'freeze_context',
           'get_resource', 'register_context']


LC_ERR_PLUGIN_LOADED = 'Plugin "{name}" already loaded.'

"""entry_points group name for plugins in setup.py"""
ENTRY_POINTS_GROUP_NAME = 'dlab.plugin'

"""Container parameter name for event dispatcher in global scope."""
CONTAINER_PARAM_EVENT_DISPATCHER = 'event_dispatcher'

"""Container parameter name for plugins list in global scope."""
CONTAINER_PARAM_PLUGINS = 'plugins'

context = Container()


class RegistryLoadException(DLabException):
    pass


def register_context(key, value):
    """Sets a parameter or an object. Objects must be defined as Closures.
    Allowing any python callable leads to difficult to debug problems as
    function names (strings) are callable (creating a function with the
    same name as an existing parameter would break your container).

    :type key: str
    :param key: The unique identifier for the parameter or object.

    :param value: The value or a closure of the parameter.
    """

    context[key] = value


def extend_context(key, call):
    """Extends an object definition. Useful when you want to extend an
    existing object definition, without necessarily loading that object.

    :type key: string
    :param key: The unique identifier for the parameter or object.

    :type call: callable
    :param call: The passed callable.

    :rtype: callable
    :return: The wrapped callable.
    """

    context.extend(key, call)


def freeze_context(key, call):
    """Protects a callable from being interpreted as a service. This is
    useful when you want to store a callable as a parameter.

    :type key: string
    :param key: The unique identifier for the parameter or object.

    :type call: function
    :param call: A callable to protect from being evaluated.

    :rtype: callable
    :return: The passed callable.
    """

    context.protect(call)
    register_context(key, call)


def get_resource(key):
    """Returns the context resource at the specified index.

    :type key: string
    :param key: The unique identifier for the parameter or object.

    :return: Resource parameter or an object.
    """

    return context[key]


def load_context():
    """Initial Load base context resources."""

    register_context(
        CONTAINER_PARAM_EVENT_DISPATCHER, lambda c: EventDispatcher())

    register_context(
        CONTAINER_PARAM_PLUGINS, lambda c: {})


def reload_context():
    """Reload base context resources."""

    context.clear()
    load_context()


def do_action(name):
    """This function invokes all functions attached to hook action.
    Hooks needs to have next naming convention <verb>.<noun>

    :type name: str
    :param name: Action name.
    """

    def wrapper(func):
        def wrapped(*args, **kwargs):
            dispatcher = get_resource(CONTAINER_PARAM_EVENT_DISPATCHER)
            dispatcher.dispatch(name)

            return func(*args, **kwargs)
        return wrapped
    return wrapper


def add_hook(name, call):
    """Actions are the hooks that the core launches at specific points during
    execution, or when specific events occur. Plugins can specify that one or
    more of its Python functions are executed at these points, using the
    Action API.
    It is possible to create new action hooks by simply calling this function,
    specifying the name of the new hook using the name parameter.
    Hooks needs to have next naming convention <verb>.<noun>

    :type name: str
    :param name: Action name.

    :type call: callable
    :param call: Code automatically invokes whenever a special action occurs.
    """

    context[CONTAINER_PARAM_EVENT_DISPATCHER].add_listener(name, call)


def load_plugins():
    """ Load external plugins."""

    for ep in pkg_resources.iter_entry_points(group=ENTRY_POINTS_GROUP_NAME):
        get_plugins = context.raw(CONTAINER_PARAM_PLUGINS)
        plugins = get_plugins(context)

        if ep.name in plugins:
            raise RegistryLoadException(
                LC_ERR_PLUGIN_LOADED.format(name=ep.name))

        extend_context(
            CONTAINER_PARAM_PLUGINS,
            lambda p, c, name=ep.name, module=ep.module_name: dict(
                p, **{name: {'bootstrap': module}}))

        func = ep.load()

        try:
            func()
        except TypeError as e:
            raise RegistryLoadException(e)
