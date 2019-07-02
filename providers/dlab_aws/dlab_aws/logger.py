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

import time
import logging

from botocore.exceptions import ClientError

from dlab_core.domain.entities import LogMessage
from dlab_core.infrastructure.logger import (
    AbstractHandler, AbstractLoggingBuilder, StreamLogging, SysLogFormatter,
    LogLevelTransformer)


class StreamCloudWatchLog:
    """Service representing Amazon CloudWatch Logs. New log stream group will
    be created per each lambda execution.

    Args:
        client: The boto3 client
        stream_group (str): Group name.
        name (str): Stream name.
    """

    def __init__(self, client, stream_group, name=None):
        self._client = client
        self._log_stream_group = stream_group
        self._service_name = name
        self._log_stream_name = None
        self._upload_sequence_token = None

    def create_log_stream(self, name):
        """Creates a log stream for the log group if not exists.

        Args:
            name (str): Name of the service.

        Return:
            str: Name of stream log.

        Raises:
            ClientError: Error during CloudWatch log stream creation.
        """

        try:
            self._client.create_log_stream(
                logGroupName=self._log_stream_group,
                logStreamName=name
            )
        except ClientError as error:
            # do not rethrow error if stream already exists
            if error.response['Error']['Code'] != \
                    'ResourceAlreadyExistsException':
                raise error

        return name

    def _get_stream_name(self):
        """Generate the stream name and create the Stream.

        Returns:
            str: Name of stream log.
        """

        if not self._log_stream_name:
            self._log_stream_name = self.create_log_stream(
                name=self._service_name
            )

        return self._log_stream_name

    def add(self, msg):
        """Add message to CloudWatch logs.

        Args:
            msg (LogMessage): Log message entity.

        Returns:
            Response: Response from CloudWatch client
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


class AWSLoggingBuilder(AbstractLoggingBuilder):
    """AWS AbstractLoggingBuilder implementation.

    Args:
        repository (StreamCloudWatchLog): Service representing Amazon
            CloudWatch Logs.
        name (str): Logger name.
        level (int): Level of logging.
    """

    def __init__(self, repository, name, level):
        self._logger = StreamLogging(name)
        self._level = LogLevelTransformer.transform(level)
        self._repository = repository

    def get_logger(self):
        """Get builder Logging.

        Returns:
            StreamLogging: AWS Stream Logging.
        """

        return self._logger

    def set_log_level(self):
        """Get Logger level.

        Returns:
            int: The logger level.
        """

        self._logger.level = self._level

    def add_cw_handler(self):
        """Add CloudWatch handler to logger.

        Returns:
            None
        """

        formatter = SysLogFormatter()

        handler = CloudWatchHandlerDecorator(self._repository)
        handler.setLevel(self._level)
        handler.setFormatter(formatter)

        self._logger.add_handler(handler)

    def add_handlers(self):
        """Add CloudWatch handlers to logger.

        Returns:
            None
        """

        self.add_cw_handler()


class CloudWatchHandlerDecorator(AbstractHandler):
    """Decorator over CloudWatch handler.

    Args:
        client (StreamCloudWatchLog): service for Amazon CloudWatch logs.
    """

    def __init__(self, client):
        self._handler = CloudWatchHandler(
            client=client
        )

    def emit(self, record):
        """Emit a record. If a formatter is specified, it is used to format the
        record.

        Args:
            record (str): Logging message.

        Returns:
            None
        """

        self._handler.emit(record)

    def set_level(self, level):
        """Set logging level.

        Args:
            level (int): Logging level.

        Returns:
            None
        """

        self._handler.setLevel(level)

    def set_formatter(self, formatter):
        """Set logging formatter.

        Args:
            formatter (SysLogFormatter): Logger formatter.

        Returns:
             None
        """

        self._handler.setFormatter(formatter)


class CloudWatchHandler(AbstractHandler):
    """CloudWatch logs handler.

    Args:
        client (StreamCloudWatchLog): service for Amazon CloudWatch logs.
    """

    def __init__(self, client):
        self._client = client

    @staticmethod
    def get_now():
        """Get current time.

        Returns:
            int: Current date.
        """

        return int(time.time()) * 1000

    def emit(self, record):
        """Emit a record. If a formatter is specified, it is used to format the
        record.

        Args:
            record (str): Logging message.

        Returns:
            Response: response from CloudWatch client.

        Raises:
            Exception: Exception occur during CloudWatch message processing.
        """

        msg = LogMessage()
        msg.message = record
        msg.timestamp = self.get_now()

        try:
            return self._client.add(msg)
        except Exception:
            return None
