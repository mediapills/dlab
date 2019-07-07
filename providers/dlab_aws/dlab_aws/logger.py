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


class CloudWatchStreamLogger:
    """Service representing Amazon CloudWatch Logs. New log stream group will
    be created per each lambda execution.

    :param client: The boto3 client.

    :type stream_group: str
    :param stream_group: Logger group name.

    :type name: str
    :param name: Stream name.
    """

    def __init__(self, client, stream_group, name=None):
        self._client = client
        self._log_stream_group = stream_group
        self._service_name = name
        self._log_stream_name = None
        self._upload_sequence_token = None

    def create_log_stream(self, name):
        """Creates a log stream for the log group if not exists.

        :type name: str
        :param name: Stream name.

        :rtype: str
        :return: Name of stream log.

        :raises: ClientError
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

        :rtype: str
        :return: Name of stream log.
        """

        if not self._log_stream_name:
            self._log_stream_name = self.create_log_stream(
                name=self._service_name
            )

        return self._log_stream_name

    @staticmethod
    def get_now():
        """Get pre formatted current time.

        :rtype: int
        :return: Current date.
        """

        return int(time.time()) * 1000

    def add(self, record):
        """Add message to CloudWatch logs.

        :type record: str
        :param record: Logging message

        :return: Response from CloudWatch client.
        """

        kwargs = {
            'logGroupName': self._log_stream_group,
            'logStreamName': self._get_stream_name(),
            'logEvents': [{
                'message': record,
                'timestamp': self.get_now()
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


# TODO implement formatter
class CloudWatchHandler(AbstractHandler):
    """CloudWatch logs handler.

    :type client: StreamCloudWatchLog
    :param client: Client for Amazon CloudWatch logs.

    :type formatter: logging.Formatter
    :param formatter: Log formatter.
    """

    # def __init__(self, client, formatter):
    def __init__(self, client):
        self._client = client
        # self._formatter = formatter

    def emit(self, message):
        """Emit a record. If a formatter is specified, it is used to format the
        record.

        :type message: str
        :param message: Logging message

        :rtype: Response
        :return: Response from CloudWatch client.
        """

        try:
            return self._client.add(message)
        except Exception:
            return None


class StreamHandlerAdapter(AbstractHandler):
    """ Adapter for StreamHandler

    :type handler: AbstractHandler
    :param handler: Logger Handler to be added.

    :type level: int
    :param level: Log level.
    """

    def __init__(self, handler, level):
        self._handler = handler
        self._level = level

    def emit(self, record):
        """Emit a record. If a formatter is specified, it is used to format the
        record.

        :param record: Message log or other log format.
        """

        self._handler.emit(record)

    @property
    def level(self):
        return self._level


class AWSLoggingBuilder(AbstractLoggingBuilder):
    """LoggingBuilder implementation for AWS cloud provider.

    :type client: StreamCloudWatchLog
    :param client: Client for Amazon CloudWatch logs.

    :type name: str
    :param name: Stream name.

    :type level: int
    :param level: Log level.
    """

    def __init__(self, client, name, level):
        self._logging = StreamLogging(name)
        self._level = LogLevelTransformer.transform(level)
        self._client = client

    def add_cw_handler(self):
        """Add CloudWatch handler to logger."""

        handler = CloudWatchHandler(self._client)
        self._logging.add_handler(StreamHandlerAdapter(
            handler,
            self._level))

    def add_handlers(self):
        """Add CloudWatch handlers to logger."""

        self.add_cw_handler()

    def set_log_level(self):
        """Set Logger level.

        Returns:
            int: The logger level.
        """

        self._logging.level = self._level

    @property
    def logging(self):
        """Logging getter as builder result

        :rtype: AbstractLogging
        :return: Logging as result of Builder execution.
        """

        return self._logging
