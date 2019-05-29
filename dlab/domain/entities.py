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


@six.add_metaclass(abc.ABCMeta)
class BaseEntity:
    pass


class LogMessage(BaseEntity):
    """Log message entity."""

    def __init__(self):
        self._message = None
        self._timestamp = None

    @property
    def message(self):
        """Get log message

        Returns:
            str: string representation of log
        """
        return self._message

    @message.setter
    def message(self, message):
        """Set log message

        Args:
            :param str message: log message

        Returns:
            None
        """
        self._message = message

    @property
    def timestamp(self):
        """Get timestamp

        Returns:
            int: timestamp
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Set timestamp

        Args:
            :param int timestamp: timestamp
        Returns:
            None
        """
        self._timestamp = timestamp
