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

from dlab_core.domain.logger import BaseLogger


@six.add_metaclass(abc.ABCMeta)
class AbstractHandler:
    """Abstract Handler implementation."""

    def emit(self, record):
        """
        Emit a record. If a formatter is specified, it is used to format the
        record.

        Args:
            record (Any):
        Returns:
            None
        """

        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class AbstractLogging:
    """
    Abstract Logger implementation. It is interface for Logger Constructor and
    can be used to decorate existing logger functionality
    """

    @abc.abstractmethod
    def log(self, level, msg, *args, **kwargs):
        """
        Logs a message with integer level lvl on this logger. The other
        arguments are interpreted as for debug().

        Args:
            level (int): Decorated logger
            msg (str): Logging message
        Returns:
            None
        """

        raise NotImplementedError

    @abc.abstractmethod
    def add_handler(self, handler):
        """
        Add logger handler.

        Args:
            handler (AbstractHandler): Logger Handler
        Returns:
            None
        """

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def handlers(self):
        """
        Get log level
        Returns:
            int Log level
        """

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def level(self):
        """
        Get log level
        Returns:
            int Log level
        """

        raise NotImplementedError

    @level.setter
    @abc.abstractmethod
    def level(self, level):
        """
        Set log level
        Args:
            level (int): Log level
        Returns:
            None
        """

        raise NotImplementedError


class LogLevelTransformer:
    """
    Log level transformer used to transform system error levels to logging
    levels.
    """

    @staticmethod
    def transform(level):
        if isinstance(level, (int, float)) and level >= 100:
            level = int(level / 10)
        elif isinstance(level, str):
            prop_level = level.upper()

            if hasattr(logging, prop_level):
                level = getattr(logging, prop_level)
            else:
                level = logging.NOTSET  # pragma: no cover

        return level


# TODO implement trace_uuid support
class SysLogFormatter(logging.Formatter):
    """
    Log Formatter which formats messages by RFC 3164 - BSD-syslog protocol.
    """

    def __init__(self):
        log_format = '[%(levelname)s] %(asctime)s - %(message)s'
        super(SysLogFormatter, self).__init__(
            fmt=log_format
        )


class Logger(BaseLogger):
    """
    Logger which work with logging.

    Args:
        logger (AbstractLogging): Decorated logger
    """

    def __init__(self, logger):

        self._logger = logger

    def log(self, level, msg, *args, **kwargs):
        """
        Logs a message with integer level lvl on this logger. The other
        arguments are interpreted as for debug().

        Args:
            level (int): Decorated logger
            msg (str): Logging message
        Returns:
            None
        """

        level = LogLevelTransformer.transform(level)

        return self._logger.log(
            level=level,
            msg=msg,
            *args,
            **kwargs
        )

    def debug(self, msg, *args, **kwargs):
        return self.log(
            level=logging.DEBUG,
            msg=msg,
            *args,
            **kwargs
        )

    def info(self, msg, *args, **kwargs):
        return self.log(
            level=logging.INFO,
            msg=msg,
            *args,
            **kwargs
        )

    def warn(self, msg, *args, **kwargs):
        return self.log(
            level=logging.WARNING,
            msg=msg,
            *args,
            **kwargs
        )

    def err(self, msg, *args, **kwargs):
        return self.log(
            level=logging.ERROR,
            msg=msg,
            *args,
            **kwargs
        )


@six.add_metaclass(abc.ABCMeta)
class AbstractLoggingBuilder:
    """Abstract Logger Builder implementation."""

    @abc.abstractmethod
    def add_handlers(self):

        raise NotImplementedError

    @abc.abstractmethod
    def set_log_level(self):

        raise NotImplementedError

    @abc.abstractmethod
    def get_logger(self):
        """
        Get Logger as builder result

        Returns:
            AbstractLogging
        """

        raise NotImplementedError


class LoggerDirector:
    """Logger Director implementation.
    Args:
        builder (AbstractLoggingBuilder): a specified logger builder
    """

    def __init__(self, builder):
        self._builder = builder

    def build(self):
        self._builder.set_log_level()
        self._builder.add_handlers()

    @property
    def logger(self):
        logger = Logger(
            logger=self._builder.get_logger()
        )
        return logger


class StreamLogging(AbstractLogging):
    """Logger which used to log messages.
    Args:
        name (str): name of the logger
    """

    def __init__(self, name):
        logging.basicConfig()
        self._logger = logging.getLogger(name)
        self._level = logging.NOTSET

    def log(self, level, msg, *args, **kwargs):
        if self._logger.isEnabledFor(level):
            msg, kwargs = self._process(msg, kwargs)
            level = int(level)
            self._logger.log(level, msg, *args, **kwargs)

    def add_handler(self, handler):
        handler_exits = False

        for h in self._logger.handlers:
            if type(h).__name__ == type(handler).__name__:
                handler_exits = True

        if not handler_exits:
            self._logger.propagate = False
            self._logger.addHandler(hdlr=handler)

    @property
    def handlers(self):
        return self._logger.handlers

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
        self._logger.setLevel(level)

    @staticmethod
    def _process(msg, kwargs):
        try:
            extra = kwargs['extra']
        except KeyError:
            extra = {}

        kwargs['extra'] = extra

        return msg, kwargs


class StreamHandlerDecorator(AbstractHandler):

    def __init__(self):
        self._handler = logging.StreamHandler()

    def emit(self, record):
        self._handler.emit(record)

    def set_level(self, level):
        self._handler.setLevel(level)

    def set_formatter(self, formatter):
        self._handler.setFormatter(formatter)


class StreamLogBuilder(AbstractLoggingBuilder):
    """Stream LogBuilder implementation.
    Args:
        name (str): name of the logger
        level (int): log level
    """

    def __init__(self, name, level):
        self._logger = StreamLogging(name)
        self._level = LogLevelTransformer.transform(level)

    def get_logger(self):
        return self._logger

    def set_log_level(self):
        self._logger.level = self._level

    def add_stream_handler(self):
        """Add Stream handler to logger
        Returns:
            None
        """

        formatter = SysLogFormatter()

        handler = StreamHandlerDecorator()
        handler.set_level(self._level)
        handler.set_formatter(formatter)
        self._logger.add_handler(handler)

    def add_handlers(self):
        self.add_stream_handler()


# TODO Finish this
# class CustomLoggerHandler(logging.Handler):
#     """Custom logger handler implementation.
#     Args:
#         handler (AbstractHandler): a specified logger handler
#         level (int): level of logging
#     """
#
#     def __init__(self, handler, level=logging.NOTSET):
#         super(CustomLoggerHandler, self).__init__(level=level)
#         self._handler = handler
#
#     def emit(self, record):
#         self._handler.emit(self.formatter.format(record))
