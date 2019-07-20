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


class HooksException(DLabException):
    pass


def do_action(name):
    """This function invokes all functions attached to hook action. It is
    possible to create new action hooks by simply calling this function,
    specifying the name of the new hook using the name parameter.
    Hooks needs to have next naming convention <verb>.<noun>

    :type name: str
    :param name: Action name.
    """

    raise NotImplementedError


def add_hook(name, call):
    """Actions are the hooks that the core launches at specific points during
    execution, or when specific events occur. Plugins can specify that one or
    more of its Python functions are executed at these points, using the
    Action API.
    Hooks needs to have next naming convention <verb>.<noun>

    :type name: str
    :param name: Action name.

    :type call: callable
    :param call: Code automatically invokes whenever a special action occurs.
    """

    raise NotImplementedError
