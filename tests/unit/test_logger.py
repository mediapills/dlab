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
import boto3
import unittest
from mock import MagicMock, Mock
from moto import mock_logs

from dlab.domain.logger import BaseLogger
from dlab.infrastructure.logger import (
    AbstractLoggingLogger, StreamLogBuilder, LoggingLogger, CustomLoggerHandler,
    LogLevelTransformer, LoggerManager, LoggerDirector
)
from dlab.infrastructure.aws.logger import StreamCloudWatchLog, AWSLogBuilder, CloudWatchHandler


@six.add_metaclass(abc.ABCMeta)
class BaseCloudWatchLoggerTestCase:

    @abc.abstractmethod
    def test_create_log_stream(self):
        pass

    @abc.abstractmethod
    def test_add(self):
        pass


class TestCloudWatchLogger(BaseCloudWatchLoggerTestCase, unittest.TestCase):
    GROUP = 'stream_log_group'
    STREAM_NAME = 'function_name'

    def setUp(self):
        self.client = boto3.client('logs')
        self.cw_logs = StreamCloudWatchLog(
            client=self.client,
            stream_group=self.GROUP,
            service_name=self.STREAM_NAME
        )

        self.msg = Mock()
        self.msg.message = 'test log message'
        self.msg.timestamp = 123

    @mock_logs
    def test_create_log_stream(self):
        self.client.create_log_group(logGroupName=self.GROUP)
        self.cw_logs.create_log_stream(self.STREAM_NAME)

        response = self.client.describe_log_streams(logGroupName=self.GROUP)

        self.assertEqual(response['logStreams'][0]['logStreamName'], self.STREAM_NAME)

    # noinspection PyTypeChecker
    @mock_logs
    def test_add(self):
        self.client.create_log_group(logGroupName=self.GROUP)
        self.cw_logs.add(self.msg)
        response = self.client.get_log_events(
            logGroupName=self.GROUP,
            logStreamName=self.STREAM_NAME,
        )
        self.assertEqual(response['events'][0]['message'], 'test log message')


class TestAWSLogBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = AWSLogBuilder(
            logger_name='Test logger',
            level=10,
            repository=StreamCloudWatchLog(
                client=boto3.client('logs'),
                stream_group='test_group',
                service_name='service_name'
            ))

    def test_get_logger(self):
        logger = self.builder.get_logger()

        self.assertIsInstance(logger, AbstractLoggingLogger)

    def test_set_log_level(self):
        self.builder.set_log_level()

        self.assertEqual(self.builder.get_logger().level, self.builder._level)

    def test_add_cw_handler(self):
        self.builder.add_cw_handler()

        self.assertEqual(1, len(self.builder.get_logger()._logger.handlers))

    def test_add_handlers(self):
        self.builder.add_handlers()

        self.assertEqual(1, len(self.builder.get_logger()._logger.handlers))


class TestCloudWatchHandler(unittest.TestCase):
    GROUP = 'stream_log_group'
    STREAM_NAME = 'function_name'
    TEST_MESSAGE = 'test log message'

    def setUp(self):
        self.client = MagicMock()
        self.client.put_log_events.return_value = self.TEST_MESSAGE

        self.handler = CloudWatchHandler(
            client=StreamCloudWatchLog(
                client=self.client,
                stream_group=self.GROUP,
                service_name=self.STREAM_NAME
            ))

        self.msg = Mock()
        self.msg.message = self.TEST_MESSAGE
        self.msg.timestamp = 123

    # noinspection PyTypeChecker
    def test_emit(self):
        response = self.handler.emit(self.msg)

        self.assertEqual(response, self.TEST_MESSAGE)


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

        self.assertEqual(2, len(self.builder.get_logger()._logger.handlers))

    def test_add_handlers(self):
        self.builder.add_handlers()

        self.assertEqual(2, len(self.builder.get_logger()._logger.handlers))


class TestLoggingLogger(unittest.TestCase):
    TEST_MESSAGE = 'test log message'

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


class TestLoggerManager(unittest.TestCase):
    TEST_MESSAGE = 'test log message'

    # noinspection PyTypeChecker
    def setUp(self):
        self.client = MagicMock()
        self.logger = LoggerManager(logger=self.client)

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
