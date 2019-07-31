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


class DispatcherExpectedCallableException(DLabException):
    """Raised when trying to call non callable object."""
    pass


class EventDispatcher:

    def __init__(self):
        self._listeners = {}

    def add_listener(self, name, call):
        """Adds an event listener that listens on the specified events.

        :type name: str
        :param name: The name of the event to dispatch.

        :type call: callable
        :param call: The passed callable.

        :raise DispatcherExpectedCallableException
        """

        if not callable(call):
            raise DispatcherExpectedCallableException(call)

        if name not in self._listeners:
            self._listeners[name] = []

        self._listeners[name].append(call)

    def get_listeners(self, name):
        """Gets the list of listeners for a specific event.

        :type name: str
        :param name: The name of the event to dispatch.

        :rtype set
        :return: List of all event listeners selected by event name.
        """

        if name not in self._listeners:
            return None

        return self._listeners[name]

    def has_listeners(self, name):
        """Checks whether an event has any registered listeners.

        :type name: str
        :param name: The name of the event to dispatch.

        :rtype: bool
        :return: True if the specified event has any listeners,
        False otherwise.
        """

        return name in self._listeners

    def dispatch(self, name):
        """Dispatches an event to all registered listeners.

        :type name: str
        :param name: The name of the event to dispatch.
        """

        if not self.has_listeners(name):
            return

        for call in self.get_listeners(name):
            call()
