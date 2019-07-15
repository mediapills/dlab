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

from dlab_core.domain.exceptions import DLabException


class RepositoryException(DLabException):
    """Base class for Repository execution exceptions."""

    pass


@six.add_metaclass(abc.ABCMeta)
class BaseRepository:
    """Base class for Repositories."""

    @abc.abstractmethod
    def find_one(self, key):
        """Find one record in storage.

        :type key: str
        :param key: Record unique identifier.

        :rtype: dict
        :return: Record data.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def find_all(self):
        """Finds all entities in the repository.

        :rtype: list of dict
        :return: All records from data storage.
        """

        raise NotImplementedError
