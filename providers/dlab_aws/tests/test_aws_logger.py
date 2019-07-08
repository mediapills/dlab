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

import boto3
import unittest

from dlab_core.infrastructure.logger import AbstractLogging, LoggerDirector
from dlab_aws.logger import (
    CloudWatchStreamLogger, CloudWatchHandler, AWSLoggingBuilder)

from mock import MagicMock
from moto import mock_logs

GROUP_NAME = 'stream_log_group'
STREAM_NAME = 'function_name'
TEST_MESSAGE = 'test message'
LOG_LEVEL = 30


class TestCloudWatchStreamLogger(unittest.TestCase):
    GROUP = 'stream_log_group'
    STREAM_NAME = 'stream_name'

    @mock_logs
    def setUp(self):
        self.client = boto3.client('logs', region_name='us-east-1')
        self.cw_logs = CloudWatchStreamLogger(
            client=self.client,
            stream_group=GROUP_NAME,
            name=STREAM_NAME
        )

    @mock_logs
    def test_create_log_stream(self):
        self.client.create_log_group(logGroupName=GROUP_NAME)
        self.cw_logs.create_log_stream(STREAM_NAME)

        response = self.client.describe_log_streams(logGroupName=GROUP_NAME)

        self.assertEqual(
            response['logStreams'][0]['logStreamName'], STREAM_NAME)

    @mock_logs
    def test_add_messages(self):
        self.client.create_log_group(logGroupName=GROUP_NAME)

        self.cw_logs.add(TEST_MESSAGE)

        response = self.client.get_log_events(
            logGroupName=GROUP_NAME,
            logStreamName=STREAM_NAME,
        )

        self.assertEqual(response['events'][0]['message'], TEST_MESSAGE)

        sequence_token = self.cw_logs._upload_sequence_token
        self.cw_logs.add(TEST_MESSAGE)

        self.assertNotEqual(
            self.cw_logs._upload_sequence_token,
            sequence_token)

    # TODO implement test_client_create_log_stream_exception test
    def test_client_create_log_stream_exception(self):
        self.assertTrue(True)


class TestCloudWatchHandler(unittest.TestCase):

    def setUp(self):
        client = MagicMock()
        client.put_log_events.return_value = TEST_MESSAGE

        self.handler = CloudWatchHandler(
            client=CloudWatchStreamLogger(
                client=client,
                stream_group=GROUP_NAME,
                name=STREAM_NAME
            ))

    def test_emit(self):
        response = self.handler.emit(TEST_MESSAGE)

        self.assertEqual(response, TEST_MESSAGE)

    def test_client_exception(self):
        self.handler._client.add = MagicMock()
        self.handler._client.add.side_effect = Exception()

        response = self.handler.emit(TEST_MESSAGE)

        self.assertIsNone(response)


class TestAWSLoggingBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = AWSLoggingBuilder(
            name='test logger',
            level=LOG_LEVEL,
            client=boto3.client('logs')
        )

    def test_get_logger(self):

        self.assertIsInstance(self.builder.logging, AbstractLogging)

    def test_set_log_level(self):
        self.builder.set_log_level()

        self.assertEqual(self.builder.logging.level, LOG_LEVEL)

    def test_add_cw_handlers(self):
        self.builder.add_handlers()

    def test_level_check(self):
        director = LoggerDirector(builder=self.builder)
        director.build()
        logger = director.logger

        a = logger.err(TEST_MESSAGE)
        b = 2
