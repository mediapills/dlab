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

import unittest
from mock import MagicMock

from dlab_core.domain.logger import BaseLogger
from dlab_core.infrastructure.logger import (
    AbstractLoggingLogger, StreamLogBuilder, LoggingLogger, CustomLoggerHandler,
    LogLevelTransformer, Logger, LoggerDirector
)


class TestStreamLogBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = StreamLogBuilder(
            logger_name='Test logger',
            level=10
        )

    def test_get_logger(self):
        logger = self.builder.get_logger()

        self.assertIsInstance(logger, AbstractLoggingLogger)

    def test_set_log_level(self):
        self.builder.set_log_level()

        self.assertEqual(self.builder.get_logger().level, self.builder._level)

    def test_add_stream_handler(self):
        self.builder.add_stream_handler()

        self.assertEqual(1, len(self.builder.get_logger()._logger.handlers))

    def test_add_handlers(self):
        self.builder.add_handlers()

        self.assertEqual(1, len(self.builder.get_logger()._logger.handlers))


class TestLoggingLogger(unittest.TestCase):
    TEST_MESSAGE = 'test log message'

    # noinspection PyTypeChecker
    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_logger.log.return_value = self.TEST_MESSAGE
        self.mock_logger.isEnabledFor.return_value = True
        self.mock_logger.hasHandlers.return_value = True

        self.logger = LoggingLogger(logger=self.mock_logger)

    def test_level(self):
        self.assertEqual(0, self.logger.level)

    def test_set_level(self):
        self.logger.level = 10
        self.assertEqual(10, self.logger.level)

    def test_log(self):
        self.logger.log(10, self.TEST_MESSAGE)

        self.mock_logger.log.assert_called_with(10, self.TEST_MESSAGE, extra={})

    def test_add_handler(self):
        handler = MagicMock()
        self.logger.add_handler(handler)

        self.mock_logger.addHandler.assert_called_with(hdlr=handler)

    def test_process(self):
        self.assertIn(self.TEST_MESSAGE, self.logger.process(self.TEST_MESSAGE, {}))


class TestCustomLoggerHandler(unittest.TestCase):

    # noinspection PyTypeChecker
    def setUp(self):
        self.client = MagicMock()
        self.handler = CustomLoggerHandler(self.client)
        self.handler.formatter = MagicMock()

    def test_emit(self):
        self.handler.emit('test')

        self.client.emit.assert_called()


class TestLogLevelTransformer(unittest.TestCase):

    def test_log_level_transformer(self):
        level = LogLevelTransformer.transform('DEBUG')

        self.assertEqual(10, level)


class TestLogger(unittest.TestCase):
    TEST_MESSAGE = 'test log message'

    # noinspection PyTypeChecker
    def setUp(self):
        self.client = MagicMock()
        self.logger = Logger(logger=self.client)

    def test_log(self):
        self.logger.log(40, self.TEST_MESSAGE)

        self.client.log.assert_called_with(level=40, msg=self.TEST_MESSAGE)

    def test_debug(self):
        self.logger.debug(self.TEST_MESSAGE)

        self.client.log.assert_called_with(level=10, msg=self.TEST_MESSAGE)

    def test_info(self):
        self.logger.info(self.TEST_MESSAGE)

        self.client.log.assert_called_with(level=20, msg=self.TEST_MESSAGE)

    def test_warn(self):
        self.logger.warn(self.TEST_MESSAGE)

        self.client.log.assert_called_with(level=30, msg=self.TEST_MESSAGE)

    def test_err(self):
        self.logger.err(self.TEST_MESSAGE)

        self.client.log.assert_called_with(level=40, msg=self.TEST_MESSAGE)


class TestLoggerDirector(unittest.TestCase):

    # noinspection PyTypeChecker
    def setUp(self):
        self.builder = MagicMock()

        self.logger_director = LoggerDirector(
            builder=self.builder
        )

    def test_build(self):
        self.logger_director.build()

        self.builder.add_handlers.assert_called()

    def test_logger(self):
        logger = self.logger_director.logger

        self.assertIsInstance(logger, BaseLogger)
