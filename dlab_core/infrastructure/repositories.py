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

# TODO add comments for all classes, properties and methods

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

# TODO remove PyUnresolvedReferences after python 3 migration
if six.PY2:
    # noinspection PyUnresolvedReferences
    from ConfigParser import ConfigParser
else:
    # noinspection PyUnresolvedReferences
    from configparser import ConfigParser


@six.add_metaclass(abc.ABCMeta)
class DictRepository(BaseRepository):

    LC_INVALID_CONTEXT_TYPE = 'Invalid context type, should be instance of {}'

    def __init__(self):
        self._data = {}

    @property
    def data(self):
        return self._data

    def find_one(self, key):
        return self.data.get(key)

    def find_all(self):
        return self.data


@six.add_metaclass(abc.ABCMeta)
class BaseLazyLoadRepository(DictRepository):

    @property
    def data(self):
        if not self._data:
            self._load_data()
        return self._data

    @abc.abstractmethod
    def _load_data(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseFileRepository(DictRepository):
    # TODO: Rename error message
    LC_NO_FILE = 'There is no file with path "{file_path}"'

    def __init__(self, absolute_path):
        super(BaseFileRepository, self).__init__()
        self._file_path = None
        self.file_path = absolute_path

    @classmethod
    def _validate(cls, file_path):
        if not isinstance(file_path, str):
            raise DLabException(
                cls.LC_INVALID_CONTEXT_TYPE.format(str.__name__)
            )

        if not os.path.isfile(file_path):
            raise DLabException(
                cls.LC_NO_FILE.format(file_path=file_path)
            )

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._validate(file_path)
        self._file_path = file_path
        self._data = {}


class ArrayRepository(DictRepository):

    def __init__(self, data=None):
        super(ArrayRepository, self).__init__()
        if data is not None:
            self._validate(data)
            self._data = data

    def append(self, key, value):
        self._data[key] = value

    def _validate(self, data):
        if not isinstance(data, dict):
            raise DLabException(
                self.LC_INVALID_CONTEXT_TYPE.format(str.__name__)
            )


# FIXME: there can be problems with find_all method for win32 platform
class EnvironRepository(DictRepository):

    def __init__(self):
        super(EnvironRepository, self).__init__()
        self._data.update(os.environ)

    def find_one(self, key):
        if sys.platform == 'win32':
            key = key.upper()
        return super(EnvironRepository, self).find_one(key)


class JSONContentRepository(DictRepository):

    LC_NOT_JSON_CONTENT = 'No JSON object could be decoded'

    def __init__(self, content=None):
        super(JSONContentRepository, self).__init__()
        self.content = content

    @property
    def content(self):

        return self._content

    @content.setter
    def content(self, content):
        if not isinstance(content, str):
            raise DLabException(
                self.LC_INVALID_CONTEXT_TYPE.format(str.__name__)
            )

        try:
            json_data = json.loads(content)
            self._data = deepcopy(json_data)
        except ValueError:
            raise DLabException(self.LC_NOT_JSON_CONTENT)

        self._content = content


class ArgumentsRepository(BaseLazyLoadRepository):

    LC_ERR_WRONG_ARGUMENTS = 'Unrecognized arguments'

    def __init__(self, arg_parse=None):
        super(ArgumentsRepository, self).__init__()
        if arg_parse is None:
            self.arg_parse = argparse.ArgumentParser()
        else:
            self.arg_parse = arg_parse

    @property
    def arg_parse(self):
        return self._arg_parse

    @arg_parse.setter
    def arg_parse(self, arg_parse):
        if not isinstance(arg_parse, argparse.ArgumentParser):
            raise DLabException(
                self.LC_INVALID_CONTEXT_TYPE.format(str.__name__)
            )

        self._arg_parse = arg_parse

    @staticmethod
    @contextmanager
    def _silence_stderr():
        new_target = open(os.devnull, "w")
        old_target = sys.stderr
        sys.stderr = new_target
        try:
            yield new_target
        finally:
            sys.stderr = old_target

    def _load_data(self):
        try:
            with self._silence_stderr():
                args = self._arg_parse.parse_args()
        except SystemExit:
            raise DLabException(self.LC_ERR_WRONG_ARGUMENTS)

        for key, val in vars(args).items():
            self._data[key] = val

    def add_argument(self, *args, **kwargs):
        self._arg_parse.add_argument(*args, **kwargs)
        self._data = {}


class ConfigRepository(BaseFileRepository, BaseLazyLoadRepository):
    VARIABLE_TEMPLATE = "{0}_{1}"

    def __init__(self, absolute_path):
        super(ConfigRepository, self).__init__(absolute_path)

    def _load_data(self):
        config = ConfigParser()
        config.read(self.file_path)
        for section in config.sections():
            for option in config.options(section):
                var = self.VARIABLE_TEMPLATE.format(section, option)
                if var not in self._data.keys():
                    self._data[var] = config.get(section, option)


class SQLiteRepository(BaseFileRepository):

    ALL_QUERY_TEMPLATE = 'SELECT {key}, {value} FROM {table}'
    ONE_QUERY_TEMPLATE = ALL_QUERY_TEMPLATE + ' where {key}=?'

    LC_READING_ERROR = 'Error while data reading with message "{msg}".'

    def __init__(self, absolute_path, table_name, key_field_name='key', value_field_name='value'):
        super(SQLiteRepository, self).__init__(absolute_path)

        # TODO: table, key and value needs to be string
        self._table_name = table_name
        self._key_field_name = key_field_name
        self._value_field_name = value_field_name

        self.__connection = None

        settings = dict(
            table=self._table_name,
            key=self._key_field_name,
            value=self._value_field_name,
        )
        self.__select_one_query = self.ONE_QUERY_TEMPLATE.format(**settings)
        self.__select_all_query = self.ALL_QUERY_TEMPLATE.format(**settings)

    @property
    def connection(self):
        if not self.__connection:
            self.__connection = sqlite3.connect(self.file_path)
        return self.__connection

    def _execute(self, query, *args):
        try:
            return self.connection.execute(query, args).fetchall()
        except sqlite3.OperationalError as e:
            raise DLabException(str(e))

    def find_one(self, key):
        data = self._execute(self.__select_one_query, key)

        for row in data:
            return row[1]
        return None

    def find_all(self):
        data = self._execute(self.__select_all_query)

        return {row[0]: row[1] for row in data}


class ChainOfRepositories(DictRepository):
    def __init__(self, repos=()):
        super(ChainOfRepositories, self).__init__()

        if not isinstance(repos, list) and not isinstance(repos, tuple):
            raise DLabException(self.LC_INVALID_CONTEXT_TYPE.format(
                "{} or {}".format(list.__name__, tuple.__name__)
            ))

        self._repos = []

        for repo in repos:
            self.register(repo)

    def register(self, repo):
        if not issubclass(type(repo), DictRepository):
            raise DLabException(
                self.LC_INVALID_CONTEXT_TYPE.format(DictRepository.__name__)
            )

        self._repos.append(repo)

    def find_one(self, key):
        for repo in self._repos:
            value = repo.find_one(key)
            if value is not None:
                return value

        return None

    def find_all(self):
        data = {}

        if len(self._repos):
            for repo in self._repos:
                data.update(repo.data)

        return data
