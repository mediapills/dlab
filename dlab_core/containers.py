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

LC_ERR_CANNOT_OVERRIDE_FROZEN = 'Cannot override frozen service "{key}".'


class ContainerException(DLabException):
    """Base Container Exceptions. Raised during container execution."""

    pass


class ContainerTypeException(ContainerException):
    """Raised when try to assign wrong data type."""

    pass


class ContainerFrozenServiceException(ContainerException):
    """Raised when try to access a key that is represent frozen data in
    a dictionary (dict).
    """

    def __init__(self, key):
        super(ContainerFrozenServiceException, self).__init__(
            LC_ERR_CANNOT_OVERRIDE_FROZEN.format(key=key)
        )


class ContainerKeyException(ContainerException):
    """Raised when try to access a key that isn't in a dictionary (dict)."""

    pass


class ContainerExpectedCallableException(ContainerException):
    """Raised when trying to call non callable object."""

    pass


class Container:
    """Instantiates the container. Objects and parameters can be passed as
    argument to the constructor.

    :type args: dict
    :param args: The parameters or objects.

    :raise ContainerTypeException: Handle wrong input data type.
    """

    def __init__(self, args=None):
        self._data = {}
        self._frozen = set()
        self._raw = {}
        self._protected = set()

        if args is None:
            args = {}
        elif not isinstance(args, dict):
            raise ContainerTypeException(type(args))

        for key in args:
            self[key] = args[key]

    def __setitem__(self, key, value):
        """Sets a parameter or an object. Objects must be defined as Closures.
        Allowing any python callable leads to difficult to debug problems as
        function names (strings) are callable (creating a function with the
        same name as an existing parameter would break your container).

        :type key: str
        :param key: The unique identifier for the parameter or object.

        :param value: The value or a closure of the parameter.

        :raise ContainerFrozenServiceException: Prevent override of a frozen
        data.
        """

        if key in self._frozen:
            raise ContainerFrozenServiceException(key)

        self._data[key] = value

    def __getitem__(self, key):
        """Gets a parameter or an object.

        :type key: string
        :param key: The unique identifier for the parameter or object.

        :return: The value of the parameter or an object.

        :raise ContainerKeyException: Do not allow to get out of scope element.
        """

        if key not in self._data:
            raise ContainerKeyException(key)

        raw = self._data[key]

        if any([
            not callable(raw),
            key in self._frozen,
            raw in self._raw,
            raw in self._protected,
        ]):
            return raw

        self._raw[key] = raw
        self._frozen.add(key)

        val = self._data[key] = raw(self)

        return val

    def keys(self):
        """Return set-like object providing a view on container keys.

        :rtype: set
        :return: Container keys list.
        """

        return self._data.keys()

    def __len__(self):
        """Count elements of an object.

        :rtype: int
        :return: The custom count as an integer.
        """

        return len(self._data)

    def __delitem__(self, key):
        """Unset element from container

        :type key: string
        :param key: The unique identifier for the parameter or object.

        :raise ContainerKeyException: Do not allow to get out of scope element.
        """

        if key not in self._data.keys():
            raise ContainerKeyException(key)

        raw = self._data[key]
        del self._data[key]

        if key in self._frozen:
            self._frozen.remove(key)

        if key in self._raw:
            del self._raw[key]

        if raw in self._protected:
            self._protected.remove(raw)

    def clear(self):
        """Remove all items from container.
        """

        self._data.clear()
        self._frozen.clear()
        self._raw.clear()
        self._protected.clear()
        # self._factories.clear()

    def __iter__(self):
        """Get an iterator from an Container object.

        :rtype: iterator
        :return: Iterator object that loops through each element in the object.
        """

        return iter(self._data)

    def raw(self, key):
        """Gets a parameter or the closure defining an object.

        :type key: string
        :param key: The unique identifier for the parameter or object.

        :return: The value of the parameter or the closure defining an object:

        :raise ContainerKeyException: Do not allow to get out of scope element.
        """

        if key not in self._data:
            raise ContainerKeyException(key)

        if key in self._raw:
            return self._raw[key]

        return self._data[key]

    def protect(self, call):
        """Protects a callable from being interpreted as a service. This is
        useful when you want to store a callable as a parameter.

        :type call: function
        :param call: A callable to protect from being evaluated.

        :rtype: callable
        :return: The passed callable.

        :raise ContainerExpectedCallableException: Protect from call non
        callable object.
        """

        if not callable(call):
            raise ContainerExpectedCallableException(call)

        self._protected.add(call)

        return call

    def factory(self, call):
        """Marks a callable as being a factory service.

        :type call: function
        :param call: A service definition to be used as a factory.

        :rtype callable
        :return: The passed callable

        :raise ContainerExpectedCallableException: Protect from call non
        callable object.
        """

        raise NotImplementedError

    def extend(self, key, call):
        """Extends an object definition. Useful when you want to extend an
        existing object definition, without necessarily loading that object.

        :type key: string
        :param key: The unique identifier for the parameter or object.

        :type call: callable
        :param call: The passed callable.

        :rtype: callable
        :return: The wrapped callable.

        :raise ContainerFrozenServiceException: Prevent extend of a frozen
        data.
        :raise ContainerExpectedCallableException: Protect from call non
        callable object.
        """

        if not callable(call):
            raise ContainerExpectedCallableException(call)

        if key in self._frozen:
            raise ContainerFrozenServiceException(key)

        factory = self.raw(key)

        self[key] = lambda c: call(factory(c), c)
