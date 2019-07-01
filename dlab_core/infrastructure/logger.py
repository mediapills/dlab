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
import time
import logging

from abc import ABCMeta, abstractmethod
from botocore.exceptions import ClientError

from dlab_core.domain.entities import LogMessage
from dlab_core.domain.logger import (
    AbstractHandler, AbstractLogBuilder, LoggingLogger,
    LogLevelTransformer, CustomLoggerHandler, SysLogFormatter
)


@six.add_metaclass(ABCMeta)
class AbstractCloudWatchLog:
    """Generic service for Amazon CloudWatch logs."""

    CLIENT_NAME = 'logs'

    @abstractmethod
    def add(self, msg):
        """Add message to CloudWatch logs
        Args:
            :param LogMessage msg: log message
        Returns:
            Response: response from CloudWatch client
        """
        pass


class AWSLogBuilder(AbstractLogBuilder):
    """AWS LogBuilder implementation.
    Args:
        repository (AbstractCloudWatchLog): Service representing Amazon CloudWatch Logs.
        logger_name (str): logger name
        level (int): level of logging
    """

    def __init__(self, repository, logger_name, level):
        logging.basicConfig()
        self._logger = LoggingLogger(
            logger=logging.getLogger(logger_name)
        )
        self._level = LogLevelTransformer.transform(level)
        self._repository = repository

    def get_logger(self):
        return self._logger

    def set_log_level(self):
        self._logger.level = self._level

    def add_cw_handler(self):
        """Add CloudWatch handler to logger
        Returns:
            None
        """
        handler = CustomLoggerHandler(
            handler=CloudWatchHandler(
                client=self._repository
            )
        )

        handler.setLevel(logging.DEBUG)
        formatter = SysLogFormatter()
        handler.setFormatter(formatter)
        self._logger.add_handler(handler)

    def add_handlers(self):
        self.add_cw_handler()


class CloudWatchHandler(AbstractHandler):
    """CloudWatch logs handler.
    Args:
        :param AbstractCloudWatchLog client: service for Amazon CloudWatch logs
    """

    def __init__(self, client):
        self._client = client

    @staticmethod
    def get_now():
        """Get current time
        Returns:
            int:
        """
        return int(time.time()) * 1000

    def emit(self, record):
        """Log the specified logging record
        Args:
            :param str record: message to be logged
        Returns:
            Response: response from CloudWatch client
        """
        msg = LogMessage()
        msg.message = record
        msg.timestamp = self.get_now()

        try:
            return self._client.add(msg)
        except Exception:
            return None


class StreamCloudWatchLog(AbstractCloudWatchLog):
    """Service representing Amazon CloudWatch Logs.
    New log stream group will be created per each lambda execution.
    Args:
        client: boto3 client
        stream_group (str): group name
        service_name (str): stream name
    """

    def __init__(self, client, stream_group, service_name=None):
        self._client = client

        self._log_stream_group = stream_group
        self._service_name = service_name
        self._log_stream_name = None

        self._upload_sequence_token = None

    def create_log_stream(self, service_name):
        """Creates a log stream for the log group if not exists
        Args:
            :param str service_name: name of the service
        Return:
            str: name of stream log
        """
        try:
            self._client.create_log_stream(
                logGroupName=self._log_stream_group,
                logStreamName=service_name
            )
        except ClientError as error:
            # do not rethrow error if stream already exists
            if error.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                raise error

        return service_name

    def _get_stream_name(self):
        """Generate the stream name and create the Stream
        Returns:
            str: name of stream log
        """
        if not self._log_stream_name:
            self._log_stream_name = self.create_log_stream(
                service_name=self._service_name
            )

        return self._log_stream_name

    def add(self, msg):
        """Add message to CloudWatch logs
        Args:
            :param LogMessage msg: log message entity
        Response:
            Response: response from CloudWatch client
        """
        kwargs = {
            'logGroupName': self._log_stream_group,
            'logStreamName': self._get_stream_name(),
            'logEvents': [{
                'message': msg.message,
                'timestamp': msg.timestamp
            }]
        }

        if self._upload_sequence_token:
            kwargs.update({
                'sequenceToken': self._upload_sequence_token
            })

        response = self._client.put_log_events(**kwargs)
        if 'nextSequenceToken' in response:
            self._upload_sequence_token = response['nextSequenceToken']

        return response
