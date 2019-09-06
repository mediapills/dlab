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

LC_ERR_ARGUMENT_TYPE_DICT = 'Argument must be of type dict.'


class RoutingException(DLabException):
    """Base class for Routing exceptions"""
    pass


class RouteArgumentTypeException(RoutingException):
    pass


class RouteArgumentKeyException(RoutingException):
    pass


class RouteArgumentValueException(RoutingException):
    pass


class RouteInvokeCallableException(RoutingException):
    pass


class CLIRoute(object):

    def __init__(self, invoke, arguments):
        """
        :type invoke:  callable
        :param invoke: method that will be invoked by router

        :type arguments:  dict
        :param arguments: command, split into an array of strings

        """
        self.invoke = invoke
        self.arguments = arguments

    @property
    def invoke(self):
        """
        :rtype invoke:  callable
        :return invoke: method that will be invoked by router

        """
        return self._invoke

    @invoke.setter
    def invoke(self, invoke):
        """
        :type invoke:  callable
        :param invoke: method that will be invoked by router
        """
        if not callable(invoke):
            raise RouteInvokeCallableException()
        self._invoke = invoke

    @property
    def arguments(self):
        """
        :rtype arguments:  dict
        :return arguments: dict of arguments, where key is index of argument
                           and value - the argument itself
        """
        return self._arguments

    @arguments.setter
    def arguments(self, arguments):
        """
        :type arguments:  dict
        :param arguments: dict of arguments, where key is index of argument
                          and value - the argument itself
        """
        if not isinstance(arguments, dict):
            raise RouteArgumentTypeException(LC_ERR_ARGUMENT_TYPE_DICT)
        for item in arguments.items():
            self.validate_arguments_dict(*item)
        self._arguments = arguments

    @staticmethod
    def validate_arguments_dict(key, value):
        if not isinstance(key, int):
            raise RouteArgumentKeyException(key)
        if not isinstance(value, str):
            raise RouteArgumentValueException(value)


class CLIRouter(object):

    def __init__(self, routes=()):
        self._routes = []
        if len(routes):
            for route in routes:
                self.add(route)

    def add(self, route):
        """
        :type route: CLIRoute
        :param route: Cli route.
        """
        if isinstance(route, CLIRoute):
            self._routes.append(route)

    def match(self, args):
        """
        :type args:  list
        :param args: command, split into an array of strings

        :rtype  Route
        :return route matched by all parameters with maximum match size

        """
        items = [r for r in self._routes if self.match_args(r.arguments, args)]
        return self.extract_maximum_match(items)

    @staticmethod
    def extract_maximum_match(routes):
        # crete list of dicts with route and sorted arguments index
        items = [{'route': r, 'indexes': sorted(r.arguments)}
                 for r in routes]
        # while route items have elements in orders indexes list
        while any(map(lambda x: x['indexes'], items)):
            # get general maximum index of all routes arguments
            max_id = max(map(lambda x: x['indexes'][-1], items))
            # pop maximum routes indexes and  filter routes,
            # that has this index equal to general maximum value
            items = list(filter(lambda x: x['indexes'].pop() == max_id, items))
        return [item['route'] for item in items]

    @staticmethod
    def match_args(route_args, cli_args):
        """

        :type route_args:  dict
        :param route_args: dict of route args

        :type cli_args:  list
        :param cli_args: cli arguments

        :rtype:  bool
        :returns True or False depending on matching cli args to routing args

        If maximum route arguments index is less then cli args count and
        values from cli equal corresponding indexes values return True

        """
        return (max(route_args) < len(cli_args) and all(
            [cli_args[index] == val for index, val in route_args.items()]))
