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
import logging

from dlab_core.domain.logger import AbstractLogger, NOTSET


class LogLevelTransformer:
    """
    Log level transformer used to transform system error levels to logging
    levels.
    """

    @staticmethod
    def transform(level):
        """Log level helper validate log level and transform to common format.

        :type level: int
        :param level: Log level.

        :rtype: int
        :return: Log level.
        """
        if isinstance(level, (int, float)) and level >= 100:
            return int(level / 10)

        if isinstance(level, str):
            level = level.upper()
            return (getattr(logging, level) if hasattr(logging, level)
                    else logging.NOTSET)  # pragma: no cover

        return level


@six.add_metaclass(abc.ABCMeta)
class AbstractHandler:
    """Abstract Handler implementation."""

    def emit(self, record):
        """Emit a record. If a formatter is specified, it is used to format the
        record.

        :param record: Message log or other log format.
        """

        raise NotImplementedError


class SimpleLoggingHandler(logging.Handler):
    """Custom logger handler implementation.

    :type handler: AbstractHandler
    :param handler: Logger handler.

    :rtype: int
    :return: Log level.
    """

    def __init__(self, handler, level=NOTSET):
        super(SimpleLoggingHandler, self).__init__(level=level)
        self._handler = handler

    def emit(self, record):
        """Emit a record. If a formatter is specified, it is used to format the
        record.

        :param record: Message log or other log format.
        """

        self._handler.emit(self.formatter.format(record))


@six.add_metaclass(abc.ABCMeta)
class AbstractLogging:
    """Wrapper and Aggregator over Logger Handler to control log level can be
    used to decorate existing logger functionality.
    """

    @property
    @abc.abstractmethod
    def level(self):
        """Log level getter.

        :rtype: int
        :return: Log level.
        """

        raise NotImplementedError

    @level.setter
    @abc.abstractmethod
    def level(self, level):
        """Log level setter.

        :type level: int
        :param level: Log level.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def log(self, level, msg, *args, **kwargs):
        """
        Logs a message with integer level lvl on this logger. The other
        arguments are interpreted as for debug().

        :type level: int
        :param level: Log level.

        :type msg: str
        :param msg: Logging message.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def add_handler(self, handler):
        """Add logger handler.

        :type handler: AbstractHandler
        :param handler: Logger Handler to be added.
        """

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def handlers(self):
        """Logger Handlers getter.

        :rtype: list of AbstractHandler
        :return: Log Handlers list.
        """

        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class AbstractLoggingBuilder:
    """AbstractLogging Builder implementation."""

    @abc.abstractmethod
    def add_handlers(self):
        """Add Logger handlers."""

        raise NotImplementedError

    @abc.abstractmethod
    def set_log_level(self):
        """Set Log level to Logger handlers"""

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def logging(self):
        """Logging getter as builder result

        :rtype: AbstractLogging
        :return: Logging as result of Builder execution.
        """

        raise NotImplementedError


class LoggerAdapter(AbstractLogger):
    """The adapter class implements AbstractLogger interface and keeps a
    reference to an Logging of the class.

    :type core: AbstractLogging
    :param core: Logger to be Decorated.
    """

    def __init__(self, core):
        self._logging = core

    def _log(self, level, msg, *args, **kwargs):
        """Logs a message with integer level lvl on this logger. The other
        arguments are interpreted as for debug().

        :type level: int
        :param level: Log level.

        :type msg: str
        :param msg: Logging message.
        """

        return self._logging.log(level=level, msg=msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Delegate an debug call to the underlying logger.

        :type msg: str
        :param msg: Logging message.
        """

        return self._log(level=logging.DEBUG, msg=msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Delegate an info call to the underlying logger.

        :type msg: str
        :param msg: Logging message.
        """

        return self._log(level=logging.INFO, msg=msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        """Delegate a warning call to the underlying logger.

        :type msg: str
        :param msg: Logging message.
        """

        return self._log(level=logging.WARNING, msg=msg, *args, **kwargs)

    def err(self, msg):
        """Delegate an error call to the underlying logger.

        :type msg: str
        :param msg: Logging message.
        """

        return self._log(level=logging.ERROR, msg=msg)


class LoggerDirector:
    """Logger Director implementation.

    :type builder: AbstractLoggingBuilder
    :param builder: Logger builder.
    """

    def __init__(self, builder):
        self._builder = builder

    def build(self):
        """Build Logging"""

        self._builder.set_log_level()
        self._builder.add_handlers()

    @property
    def logger(self):
        """Logger getter as result of builder building.

        :rtype: AbstractLogger
        :return: Logger
        """
        logger = LoggerAdapter(
            self._builder.logging
        )

        return logger


class StreamHandlerAdapter(AbstractHandler):
    """ Decorator over StreamHandler

    :type level: int
    :param level: Log level.

    :type formatter: logging.Formatter
    :param formatter: Log formatter.
    """

    def __init__(self, level, formatter):
        self._handler = logging.StreamHandler()
        self._handler.setLevel(level)
        self._handler.setFormatter(formatter)

    def emit(self, record):
        """Emit a record. If a formatter is specified, it is used to format the
        record.

        :param record: Message log or other log format.
        """

        self._handler.emit(record)


class StreamLogging(AbstractLogging):
    """Logger which used to log messages.

    :type name: str
    :param name: Name of the logger
    """

    def __init__(self, name):
        logging.basicConfig()
        self._logger = logging.getLogger(name)
        self._level = logging.NOTSET

    @property
    def level(self):
        """Log level getter.

        :rtype: int
        :return: Log level.
        """

        return self._level

    @level.setter
    def level(self, level):
        """Log level setter.

        :type level: int
        :param level: Log level.
        """

        self._level = level
        self._logger.setLevel(level)

    @staticmethod
    def _process(msg, kwargs):
        """Pre process log message.

        :type msg: str
        :param msg: Logging message.

        :type kwargs: dict
        :param kwargs: Logging options.
        """

        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        return msg, kwargs

    def log(self, level, msg, *args, **kwargs):
        """
        Logs a message with integer level lvl on this logger. The other
        arguments are interpreted as for debug().

        :type level: int
        :param level: Log level.

        :type msg: str
        :param msg: Logging message.
        """

        if self._logger.isEnabledFor(level):
            msg, kwargs = self._process(msg, kwargs)
            level = int(level)
            self._logger.log(level, msg, *args, **kwargs)

    def add_handler(self, handler):
        """Add logger handler.

        :type handler: AbstractHandler
        :param handler: Logger Handler to be added.
        """

        handler_exits = False

        for h in self._logger.handlers:
            if type(h).__name__ == type(handler).__name__:
                handler_exits = True

        if not handler_exits:
            self._logger.propagate = False
            self._logger.addHandler(hdlr=handler)

    @property
    def handlers(self):
        """Logger Handlers getter.

        :rtype: list of AbstractHandler
        :return: Log Handlers list.
        """

        return self._logger.handlers


class SysLogFormatter(logging.Formatter):
    """Log Formatter which formats messages by RFC 3164 - BSD-syslog protocol.
    """

    def __init__(self):
        log_format = '[%(levelname)s] %(asctime)s - %(message)s'
        super(SysLogFormatter, self).__init__(
            fmt=log_format
        )


class StreamLogBuilder(AbstractLoggingBuilder):
    """Stream LogBuilder implementation.

    :type name: str
    :param name: Logger name.

    :type level: int
    :param level: Log level.
    """

    def __init__(self, name, level):
        self._logging = StreamLogging(name)
        self._level = LogLevelTransformer.transform(level)

    def add_stream_handler(self):
        """Add Stream handler to logger"""

        handler = StreamHandlerAdapter(
            self._level,
            SysLogFormatter())

        self._logging.add_handler(handler)

    def add_handlers(self):
        """Add Logger handlers."""

        self.add_stream_handler()

    def set_log_level(self):
        """Set Log level to Logger handlers"""

        self._logging.level = self._level

    @property
    def logging(self):
        """Logging getter as builder result

        :rtype: AbstractLogging
        :return: Logging as result of Builder execution.
        """

        return self._logging
