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
import sys

from contextlib import contextmanager
from copy import deepcopy
from dlab_core.domain.repositories import BaseRepository, RepositoryException

LC_ERR_WRONG_ARGUMENTS = 'Unrecognized arguments'
LC_ERR_INVALID_DATA_TYPE = 'Invalid context type, should be instance of {name}'
LC_ERR_NO_FILE = 'No such file or directory: "{location}".'
LC_ERR_NOT_JSON_CONTENT = 'No JSON object could be decoded'

# TODO remove condition after Python 2.7 retirement
if six.PY2:
    # noinspection PyUnresolvedReferences
    from ConfigParser import ConfigParser  # pragma: no cover
else:
    # noinspection PyUnresolvedReferences
    from configparser import ConfigParser


class RepositoryDataTypeException(RepositoryException):
    """Raised when try to assign wrong data type.

    :type name: str
    :param name: Type name.
    """

    def __init__(self, name):
        super(RepositoryDataTypeException, self).__init__(
            LC_ERR_INVALID_DATA_TYPE.format(name=name)
        )


class RepositoryFileNotFoundException(RepositoryException):
    """Raised when try to read unavailable file.

    :type key: str
    :param key: File location
    """

    def __init__(self, key):
        super(RepositoryFileNotFoundException, self).__init__(
            LC_ERR_NO_FILE.format(location=key)
        )


class RepositoryJSONContentException(RepositoryException):
    """Raised during non JSON content serialization."""

    def __init__(self):
        super(RepositoryJSONContentException, self).__init__(
            LC_ERR_NOT_JSON_CONTENT
        )


class RepositoryWrongArgumentException(RepositoryException):
    """Raised during non JSON content serialization."""

    def __init__(self):
        super(RepositoryWrongArgumentException, self).__init__(
            LC_ERR_WRONG_ARGUMENTS
        )


@six.add_metaclass(abc.ABCMeta)
class DictRepository(BaseRepository):
    """Dictionary repository. Can be used as a base for repositories data based
    on dict.
    """

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

    def __init__(self, location):
        super(BaseFileRepository, self).__init__()
        self._location = None
        self.location = location

    @classmethod
    def _validate(cls, location):
        """Validate file location.

        :raise RepositoryDataTypeException:
        :raise RepositoryFileNotFoundException:
        """

        if not isinstance(location, str):
            raise RepositoryDataTypeException(str.__name__)

        if not os.path.isfile(location):
            raise RepositoryFileNotFoundException(location)

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

    @staticmethod
    def _validate(data):
        """Data source validator.

        :param data: Data for validation.

        :raise RepositoryDataTypeException:
        """

        if not isinstance(data, dict):
            raise RepositoryDataTypeException(str.__name__)


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

        :raise RepositoryDataTypeException:
        :raise RepositoryJSONContentException:
        """
        if not isinstance(content, str):
            raise RepositoryDataTypeException(str.__name__)

        try:
            json_data = json.loads(content)
            self._data = deepcopy(json_data)
        except ValueError:
            raise RepositoryJSONContentException()

        self._content = content


class ArgumentsRepository(BaseLazyLoadRepository):
    """ Repository based on CLI arguments as data source.

    :type arg_parse: argparse.ArgumentParser
    :param arg_parse: Argument Parser.
    """

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

        :raise RepositoryDataTypeException:
        """

        if not isinstance(arg_parse, argparse.ArgumentParser):
            raise RepositoryDataTypeException(str.__name__)

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
            sys.stderr.close()
            sys.stderr = old_target

    def _load_data(self):
        """Load data from data source.

        :rtype: list of dict
        :return: Repository data.

        :raise RepositoryWrongArgumentException:
        """

        try:
            with self._silence_stderr():
                args = self._arg_parse.parse_args()
        except SystemExit:
            raise RepositoryWrongArgumentException()

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
                self._data[var] = self._data.get(var,
                                                 config.get(section, option))


class ChainOfRepositories(DictRepository):
    """List of repositories executed one by one till data will be found.

    :type repos: list of BaseRepository.
    :param repos: List of repositories executed in chain.

    :raise RepositoryDataTypeException:
    """

    def __init__(self, repos=()):
        super(ChainOfRepositories, self).__init__()

        if not isinstance(repos, list) and not isinstance(repos, tuple):
            raise RepositoryDataTypeException("{} or {}".format(
                list.__name__,
                tuple.__name__)
            )

        self._repos = []

        for repo in repos:
            self.register(repo)

    def register(self, repo):
        """Register new repository in chain.

        :type repo: BaseRepository
        :param repo: Repository.

        :raise RepositoryDataTypeException:
        """

        if not issubclass(type(repo), DictRepository):
            raise RepositoryDataTypeException(DictRepository.__name__)

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
