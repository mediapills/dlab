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

import six
import logging
from abc import ABCMeta, abstractmethod

from dlab.domain.logger import BaseLogger


@six.add_metaclass(ABCMeta)
class AbstractLoggingLogger:
    """Abstract Logger implementation."""

    LEVEL_CRITICAL = logging.CRITICAL
    LEVEL_FATAL = LEVEL_CRITICAL
    LEVEL_ERROR = logging.ERROR
    LEVEL_WARNING = logging.WARNING
    LEVEL_WARN = LEVEL_WARNING
    LEVEL_INFO = logging.INFO
    LEVEL_DEBUG = logging.DEBUG
    LEVEL_NOTSET = logging.NOTSET

    @abstractmethod
    def log(self, level, msg, *args, **kwargs):
        pass

    @abstractmethod
    def add_handler(self, handler):
        pass

    @property
    @abstractmethod
    def level(self):
        pass

    @level.setter
    @abstractmethod
    def level(self, level):
        pass


@six.add_metaclass(ABCMeta)
class AbstractLogBuilder:
    """Abstract Logger Builder implementation."""

    @abstractmethod
    def add_handlers(self):
        pass


@six.add_metaclass(ABCMeta)
class AbstractHandler:
    """Abstract Handler implementation."""

    def emit(self, record):
        pass


class StreamLogBuilder(AbstractLogBuilder):
    """Stream LogBuilder implementation.

    Args:
        logger_name (str): name of the logger
        level (int): log level
    """

    def __init__(self, logger_name, level):
        logging.basicConfig()
        self._logger = LoggingLogger(
            logger=logging.getLogger(logger_name)
        )
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
        handler = logging.StreamHandler()
        handler.setLevel(self._level)
        formatter = SysLogFormatter()
        handler.setFormatter(formatter)
        self._logger.add_handler(handler)

    def add_handlers(self):
        self.add_stream_handler()


class LoggingLogger(AbstractLoggingLogger):
    """Logger which used to log messages.

    Args:
        logger (Logger): a logger with the specified name
    """

    def __init__(self, logger):
        self._logger = logger
        self._level = AbstractLoggingLogger.LEVEL_NOTSET

    def log(self, level, msg, *args, **kwargs):
        if self._logger.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
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
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
        self._logger.setLevel(level)

    def process(self, msg, kwargs):
        try:
            extra = kwargs['extra']
        except KeyError:
            extra = {}

        kwargs['extra'] = extra

        return msg, kwargs


class CustomLoggerHandler(logging.Handler):
    """Custom logger handler implementation.

    Args:
        handler (AbstractHandler): a specified logger handler
        level (int): level of logging
    """

    def __init__(self, handler, level=AbstractLoggingLogger.LEVEL_NOTSET):
        super(CustomLoggerHandler, self).__init__(level=level)
        self._handler = handler

    def emit(self, record):
        self._handler.emit(self.formatter.format(record))


class SysLogFormatter(logging.Formatter):
    """Log Formatter which formats messages by RFC 3164 - BSD-syslog protocol."""

    def __init__(self):
        log_format = "[%(levelname)s] %(asctime)s - %(message)s"
        super(SysLogFormatter, self).__init__(
            fmt=log_format
        )


class LogLevelTransformer:
    """Log level transformer used to transform system error levels to logging levels."""

    @staticmethod
    def transform(level):
        if isinstance(level, (int, float)) and level >= 100:
            level = int(level / 10)
        elif isinstance(level, str):
            prop_level = 'LEVEL_' + level.upper()

            if hasattr(AbstractLoggingLogger, prop_level):
                level = getattr(AbstractLoggingLogger, prop_level)
            else:
                level = AbstractLoggingLogger.LEVEL_NOTSET

        return level

    @staticmethod
    def reverse_transform(level):
        return level * 10


class LoggerManager(BaseLogger):
    """Logger Manager which work with logging.

    Args:
        logger (AbstractLoggingLogger): a specified logger which used to log messages
    """

    def __init__(self, logger):
        self._logger = logger

    def log(self, level, msg, *args, **kwargs):
        level = LogLevelTransformer.transform(level)
        return self._logger.log(
            level=level,
            msg=msg,
            *args,
            **kwargs
        )

    def debug(self, msg, *args, **kwargs):
        return self.log(
            level=AbstractLoggingLogger.LEVEL_DEBUG,
            msg=msg,
            *args,
            **kwargs
        )

    def info(self, msg, *args, **kwargs):
        return self.log(
            level=AbstractLoggingLogger.LEVEL_INFO,
            msg=msg,
            *args,
            **kwargs
        )

    def warn(self, msg, *args, **kwargs):
        return self.log(
            level=AbstractLoggingLogger.LEVEL_WARN,
            msg=msg,
            *args,
            **kwargs
        )

    def err(self, msg, *args, **kwargs):
        return self.log(
            level=AbstractLoggingLogger.LEVEL_ERROR,
            msg=msg,
            *args,
            **kwargs
        )


class LoggerDirector:
    """Logger Director implementation.

    Args:
        builder (AbstractLogBuilder): a specified logger builder
    """
    def __init__(self, builder):
        self._builder = builder

    def build(self):
        self._builder.set_log_level()
        self._builder.add_handlers()

    @property
    def logger(self):
        logger = LoggerManager(
            logger=self._builder.get_logger()
        )
        return logger
