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

import logging
import re
import unittest

from dlab_core.domain import logger as val
from dlab_core.infrastructure import logger
from mock import MagicMock


# TODO implement test for logging without prop_level attribute
class TestLogLevelTransformer(unittest.TestCase):

    def test_level_transformer(self):
        level = logger.LogLevelTransformer.transform(val.DEBUG)

        self.assertEqual(10, level)

    def test_level_transformer_gt_100(self):
        level = logger.LogLevelTransformer.transform(1001)

        self.assertEqual(100, level)


class TestSimpleLoggingHandler(unittest.TestCase):

    def test_emit(self):
        client = MagicMock()
        handler = logger.SimpleLoggingHandler(client)
        handler.formatter = MagicMock()

        handler.emit('test')

        client.emit.assert_called()


class TestLoggerAdapter(unittest.TestCase):
    TEST_MESSAGE = 'test message'

    def setUp(self):
        self.logging = MagicMock()
        self.logger = logger.LoggerAdapter(self.logging)

    def test_debug(self):
        self.logger.debug(self.TEST_MESSAGE)

        self.logging.log.assert_called_with(
            level=val.DEBUG,
            msg=self.TEST_MESSAGE
        )

    def test_info(self):
        self.logger.info(self.TEST_MESSAGE)

        self.logging.log.assert_called_with(
            level=val.INFO,
            msg=self.TEST_MESSAGE
        )

    def test_warn(self):
        self.logger.warn(self.TEST_MESSAGE)

        self.logging.log.assert_called_with(
            level=val.WARNING,
            msg=self.TEST_MESSAGE
        )

    def test_err(self):
        self.logger.err(self.TEST_MESSAGE)

        self.logging.log.assert_called_with(
            level=val.ERROR,
            msg=self.TEST_MESSAGE
        )


# TODO implement TestLoggerDirector tests for full coverage
class TestLoggerDirector(unittest.TestCase):
    pass


class TestStreamHandlerAdapter(unittest.TestCase):

    def test_constructor(self):
        formatter = logging.Formatter()
        handler = logger.StreamHandlerAdapter(
            level=logging.NOTSET,
            formatter=formatter)

        self.assertIsInstance(handler._handler, logging.StreamHandler)


class TestStreamLogging(unittest.TestCase):
    TEST_MESSAGE = 'test message'

    def setUp(self):
        self.logger = logger.StreamLogging('test')

    def test_get_level(self):
        self.assertEqual(0, self.logger.level)

    def test_set_level(self):
        self.logger.level = 10
        self.assertEqual(10, self.logger.level)

    def test_log(self):
        mck = MagicMock()
        mck.log.return_value = self.TEST_MESSAGE
        mck.isEnabledFor.return_value = True
        mck.hasHandlers.return_value = True
        logger_mock = mck

        obj = logger.StreamLogging('test')
        obj._logger = mck

        obj.log(10, self.TEST_MESSAGE)

        logger_mock.log.assert_called_with(
            10, self.TEST_MESSAGE, extra={})

    def test_handlers(self):
        formatter = logging.Formatter()
        handler = logger.StreamHandlerAdapter(val.DEBUG, formatter)
        self.logger.add_handler(handler)

        self.assertEqual(1, len(self.logger.handlers))

        self.logger.add_handler(handler)

        self.assertEqual(1, len(self.logger.handlers))


class TestSysLogFormatter(unittest.TestCase):

    def test_constructor(self):
        formatter = logger.SysLogFormatter()

        record = logging.LogRecord('request_filter', 10, '/fake/path', 123,
                                   'test message', (), None)
        pattern = re.compile('^\\[DEBUG\\] .* - test message$')

        self.assertTrue(pattern.match(
            formatter.format(record)))


class TestStreamLogBuilder(unittest.TestCase):

    LOG_LEVEL = 20

    def setUp(self):
        self.builder = logger.StreamLogBuilder(
            name='Test logger',
            level=self.LOG_LEVEL
        )

    def test_get_logger(self):

        self.assertIsInstance(
            self.builder.logging,
            logger.AbstractLogging)

    def test_set_log_level(self):
        self.builder.set_log_level()

        self.assertEqual(self.builder.logging.level, self.LOG_LEVEL)

    def test_add_handlers(self):
        self.builder.add_handlers()

        self.assertEqual(len(self.builder.logging.handlers), 1)
