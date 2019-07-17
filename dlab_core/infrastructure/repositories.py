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
import argparse
import json
import os
import six
import sqlite3
import sys

from contextlib import contextmanager
from copy import deepcopy
from dlab_core.domain.exceptions import DLabException
from dlab_core.domain.repositories import BaseRepository

# TODO remove condition after Python 2.7 retirement
if six.PY2:
    # noinspection PyUnresolvedReferences
    from ConfigParser import ConfigParser  # pragma: no cover
else:
    # noinspection PyUnresolvedReferences
    from configparser import ConfigParser


class RepositoryException(DLabException):
    """Repository exceptions."""
    pass


@six.add_metaclass(abc.ABCMeta)
class DictRepository(BaseRepository):
    """Dictionary repository. Can be used as a base for repositories data based
    on dict.
    """

    LC_INVALID_CONTEXT_TYPE = 'Invalid context type, should be instance of {}'

    def __init__(self):
        self._data = {}

    @property
    def data(self):
        """Repository data getter.

        :rtype: dict of Tuple
        :return: Repository data.
        """

        return self._data

    def find_one(self, key):
        """Find one record in storage.

        :type key: str
        :param key: Record unique identifier.

        :rtype: dict
        :return: Record data.
        """

        return self.data.get(key)

    def find_all(self):
        """Finds all entities in the repository.

        :rtype: list of dict
        :return: All records from data storage.
        """

        return self.data


@six.add_metaclass(abc.ABCMeta)
class BaseLazyLoadRepository(DictRepository):

    @property
    def data(self):
        """Repository data getter.

        :rtype: list of dict
        :return: Repository data.
        """

        if not self._data:
            self._load_data()
        return self._data

    @abc.abstractmethod
    def _load_data(self):
        """Load data from data source.

        :rtype: list of dict
        :return: Repository data.
        """

        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class BaseFileRepository(DictRepository):
    """Repository based on file data.

    :type location: str
    :param location: Data source file location.
    """

    # FIXME: Rename error message
    LC_NO_FILE = 'There is no file with path "{location}"'

    def __init__(self, location):
        super(BaseFileRepository, self).__init__()
        self._location = None
        self.location = location

    @classmethod
    def _validate(cls, location):
        """Validate file location.

        :raises: RepositoryException
        """

        if not isinstance(location, str):
            raise RepositoryException(
                cls.LC_INVALID_CONTEXT_TYPE.format(str.__name__)
            )

        if not os.path.isfile(location):
            raise RepositoryException(
                cls.LC_NO_FILE.format(location=location)
            )

    @property
    def location(self):
        """File location getter.

        :rtype: str
        :return: File location.
        """

        return self._location

    @location.setter
    def location(self, location):
        """File location setter.

        :type location: str
        :param location: File location.
        """

        self._validate(location)
        self._location = location
        self._data = {}


class ArrayRepository(DictRepository):
    """Repository based on dict data.

    :type data: dict
    :param data: Repository data.
    """

    def __init__(self, data=None):
        super(ArrayRepository, self).__init__()
        if data is not None:
            self._validate(data)
            self._data = data

    def append(self, key, value):
        """Add new element into data set.

        :type key: str
        :param key: Record UUID.

        :param value: Record value.
        """
        self._data[key] = value

    def _validate(self, data):
        """Data source validator.

        :param data: Data for validation.

        :raises: RepositoryException
        """

        if not isinstance(data, dict):
            raise RepositoryException(
                self.LC_INVALID_CONTEXT_TYPE.format(str.__name__)
            )


# FIXME: there can be problems with find_all method for win32 platform
class EnvironRepository(DictRepository):
    """Repository based on os.environ data."""

    def __init__(self):
        super(EnvironRepository, self).__init__()
        self._data.update(os.environ)

    def find_one(self, key):
        """Find one record in storage.

        :type key: str
        :param key: Record unique identifier.

        :rtype: dict
        :return: Record data.
        """

        if sys.platform == 'win32':
            key = key.upper()  # pragma: no cover
        return super(EnvironRepository, self).find_one(key)


class JSONContentRepository(DictRepository):
    """Repository based on JSON data.

    :type content: str
    :param content: JSON content for data source.
    """

    LC_NOT_JSON_CONTENT = 'No JSON object could be decoded'

    def __init__(self, content=None):
        super(JSONContentRepository, self).__init__()
        self.content = content

    @property
    def content(self):
        """Content getter.

        :rtype: str
        :returns: JSON data content.
        """

        return self._content

    @content.setter
    def content(self, content):
        """Content setter.

        :type content: str
        :param content: JSON data content.

        :raises: RepositoryException
        """
        if not isinstance(content, str):
            raise RepositoryException(
                self.LC_INVALID_CONTEXT_TYPE.format(str.__name__)
            )

        try:
            json_data = json.loads(content)
            self._data = deepcopy(json_data)
        except ValueError:
            raise RepositoryException(self.LC_NOT_JSON_CONTENT)

        self._content = content


class ArgumentsRepository(BaseLazyLoadRepository):
    """ Repository based on CLI arguments as data source.

    :type arg_parse: argparse.ArgumentParser
    :param arg_parse: Argument Parser.
    """

    LC_ERR_WRONG_ARGUMENTS = 'Unrecognized arguments'

    def __init__(self, arg_parse=None):
        super(ArgumentsRepository, self).__init__()
        self.arg_parse = arg_parse or argparse.ArgumentParser()

    @property
    def arg_parse(self):
        """Argument parser getter.

        :rtype: argparse.ArgumentParser
        :returns: Argument Parser.
        """

        return self._arg_parse

    @arg_parse.setter
    def arg_parse(self, arg_parse):
        """Argument parser setter.

        :type arg_parse: argparse.ArgumentParser
        :param arg_parse: Argument Parser.
        """

        if not isinstance(arg_parse, argparse.ArgumentParser):
            raise RepositoryException(
                self.LC_INVALID_CONTEXT_TYPE.format(str.__name__)
            )

        self._arg_parse = arg_parse

    @staticmethod
    @contextmanager
    def _silence_stderr():
        """Turn off stderr."""

        new_target = open(os.devnull, "w")
        old_target = sys.stderr
        sys.stderr = new_target
        try:
            yield new_target
        finally:
            sys.stderr = old_target

    def _load_data(self):
        """Load data from data source.

        :rtype: list of dict
        :return: Repository data.

        :raises: RepositoryException
        """

        try:
            with self._silence_stderr():
                args = self._arg_parse.parse_args()
        except SystemExit:
            raise RepositoryException(self.LC_ERR_WRONG_ARGUMENTS)

        for key, val in vars(args).items():
            self._data[key] = val

    def add_argument(self, *args, **kwargs):
        """Add argument parser argument."""

        self._arg_parse.add_argument(*args, **kwargs)
        self._data = {}


class ConfigRepository(BaseFileRepository, BaseLazyLoadRepository):
    """Repository based on file data.

    :type location: str
    :param location: Data source file location.
    """

    VARIABLE_TEMPLATE = "{0}_{1}"

    def __init__(self, location):
        super(ConfigRepository, self).__init__(location)

    def _load_data(self):
        """Load data from data source.

        :rtype: list of dict
        :return: Repository data.
        """

        config = ConfigParser()
        config.read(self.location)
        for section in config.sections():
            for option in config.options(section):
                var = self.VARIABLE_TEMPLATE.format(section, option)
                if var not in self._data:
                    self._data[var] = config.get(section, option)


class SQLiteRepository(BaseFileRepository):
    """Repository based on file data.

    :type location: str
    :param location: Data source file location.

    :type table_name: str
    :param table_name: Data source table name.

    :type key_field_name: str
    :param key_field_name: UUID field name.
    """

    ALL_QUERY_TEMPLATE = 'SELECT {key}, {value} FROM {table}'
    ONE_QUERY_TEMPLATE = ALL_QUERY_TEMPLATE + ' where {key}=?'

    LC_READING_ERROR = 'Error while data reading with message "{msg}".'

    def __init__(self, location, table_name, key_field_name='key',
                 value_field_name='value'):
        super(SQLiteRepository, self).__init__(location)

        # TODO: add validation table, key and value needs to be string
        self._table_name = table_name
        self._key_field_name = key_field_name
        self._value_field_name = value_field_name

        self.__connection = None

        settings = {
            'table': self._table_name,
            'key': self._key_field_name,
            'value': self._value_field_name,
        }
        self.__select_one_query = self.ONE_QUERY_TEMPLATE.format(**settings)
        self.__select_all_query = self.ALL_QUERY_TEMPLATE.format(**settings)

    @property
    def connection(self):
        """sqlite3 connection getter."""

        if not self.__connection:
            self.__connection = sqlite3.connect(self.location)
        return self.__connection

    def _execute(self, query, *args):
        """Execute sqlite3 query.

        :type query: str
        :param query: SQL statement.

        :raises: RepositoryException
        """

        try:
            return self.connection.execute(query, args).fetchall()
        except sqlite3.OperationalError as e:
            raise RepositoryException(str(e))

    def find_one(self, key):
        """Find one record in storage.

        :type key: str
        :param key: Record unique identifier.

        :rtype: dict
        :return: Record data.
        """

        data = self._execute(self.__select_one_query, key)

        for row in data:
            return row[1]
        return None

    def find_all(self):
        """Finds all entities in the repository.

        :rtype: dict
        :return: All records from data storage.
        """

        data = self._execute(self.__select_all_query)

        return dict(data)


class ChainOfRepositories(DictRepository):
    """List of repositories executed one by one till data will be found.

    :type repos: list of BaseRepository.
    :param repos: List of repositories executed in chain.

    :raises: RepositoryException
    """

    def __init__(self, repos=()):
        super(ChainOfRepositories, self).__init__()

        if not isinstance(repos, (list, tuple)):
            raise RepositoryException(self.LC_INVALID_CONTEXT_TYPE.format(
                "{} or {}".format(list.__name__, tuple.__name__)
            ))

        self._repos = []

        for repo in repos:
            self.register(repo)

    def register(self, repo):
        """Register new repository in chain.

        :type repo: BaseRepository
        :param repo: Repository.

        :raises: RepositoryException
        """

        if not issubclass(type(repo), DictRepository):
            raise RepositoryException(
                self.LC_INVALID_CONTEXT_TYPE.format(DictRepository.__name__)
            )

        self._repos.append(repo)

    def find_one(self, key):
        """Find one record in storage.

        :type key: str
        :param key: Record unique identifier.

        :rtype: dict
        :return: Record data.
        """

        for repo in self._repos:
            value = repo.find_one(key)
            if value is not None:
                return value

        return None

    def find_all(self):
        """Finds all entities in the repository.

        :rtype: list of dict
        :return: All records from data storage.
        """

        data = {}

        if len(self._repos):
            for repo in self._repos:
                data.update(repo.data)

        return data
