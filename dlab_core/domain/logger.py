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

from dlab_core.domain.exceptions import DLabException

CRITICAL = 50
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0


class LoggerException(DLabException):
    """Base class for Logger execution exceptions."""

    pass


@six.add_metaclass(abc.ABCMeta)
class AbstractLogger:
    """Base class for Loggers."""

    @abc.abstractmethod
    def debug(self, msg):
        """Delegate an debug call to the underlying logger.

        :type msg: str
        :param msg: Logging message.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def info(self, msg):
        """Delegate an info call to the underlying logger.

        :type msg: str
        :param msg: Logging message.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def warn(self, msg):
        """Delegate a warning call to the underlying logger.

        :type msg: str
        :param msg: Logging message.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def err(self, msg):
        """Delegate an error call to the underlying logger.

        :type msg: str
        :param msg: Logging message.
        """

        raise NotImplementedError
