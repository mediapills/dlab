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
import os
import six
import sys
from setuptools import find_packages

from dlab_core.domain.exceptions import DLabException

""" author of the package email address """
AUTHOR_EMAIL = 'dev@dlab.apache.org'

""" author of the package """
AUTHOR = 'Apache Software Foundation'

"""
Gives the index and pip some additional metadata about your package. In this
case, the package is only compatible with Python 3, is licensed under the MIT
license, and is OS-independent. You should always include at least which
version(s) of Python your package works on, which license your package is
available under, and which operating systems your package will work on. For a
complete list of classifiers, see https://pypi.org/classifiers/.
"""
CLASSIFIERS = [
    "Development Status :: 1 - Planning  ",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Build Tools",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Clustering",
    "Topic :: System :: Software Distribution",
    "Topic :: System :: Systems Administration",
]

"""
Type of markup is used for the long description. In this case, it's Markdown.
"""
DESCRIPTION_CONTENT_TYPE = "text/markdown"

"""
Text indicating the license covering the package where the license is not a
selection from the "License" Trove classifiers. See the Classifier field.
Notice that there's a licence distribution option which is deprecated but still
acts as an alias for license.
"""
LICENSE = 'Apache-2.0'

"""
Appropriate PEP 440 version specifier string will prevent pip from installing
the project on other Python versions
"""
PYTHON_REQUIRES = ', '.join([
    '>=2.7',
    '!=3.0.*',
    '!=3.1.*',
    '!=3.2.*',
    '!=3.3.*'
])

"""
URL for the homepage of the project. For many projects, this will just be a
link to GitHub, GitLab, Bitbucket, or similar code hosting service.
"""
URL = "https://github.com/apache/incubator-dlab"

""" Version file name location """
VERSION_FILE = '__version__.py'

""" Readme file location """
README_FILE = 'README.md'

""" requirements.txt file location """
REQUIREMENTS_FILE = 'requirements.txt'


class DLabSetupException(DLabException):
    """Class for DLab Setup exceptions."""
    pass


class Director:
    """
    Construct an parameters dict using the Builder interface.
    """

    def __init__(self):
        self._builder = None

    def build(self, builder):
        self._builder = builder  # type: ParametersBuilder

        self._builder.set_packages()
        self._builder.set_requirements()
        self._builder.set_version()
        self._builder.set_long_description()
        # self._builder.set_entry_points()

    @property
    def parameters(self):
        builder = self._builder  # type: ParametersBuilder
        return builder.parameters


@six.add_metaclass(abc.ABCMeta)
class ParametersBuilder:
    """
    Specify an abstract interface for creating parts of a setup parameters dict
    """

    def __init__(self, name, description):
        """
        Builder constructor

        :param name: str Distribution name of your package
        :param description: str Short, one-sentence summary of the package
        """

        self._name = name
        self._parameters = {
            'name': self._name,
            'description': description,
            'classifiers': CLASSIFIERS,
            'url': URL,
            'author': AUTHOR,
            'author_email': AUTHOR_EMAIL,
            'license': LICENSE,
            'python_requires': PYTHON_REQUIRES,
            'long_description_content_type': DESCRIPTION_CONTENT_TYPE
        }

    @property
    def name(self):
        return self._name

    @property
    def parameters(self):
        return self._parameters

    @staticmethod
    def _read_file(name):
        """
        Get content by filename

        :param name: str File name
        :return: str
        """

        if not os.path.isfile(name):
            raise DLabSetupException("No such file or directory: '{}'".format(
                name
            ))

        try:
            with open(name, "r") as fh:
                return fh.read()
        except IOError as e:
            if hasattr(e, 'filename'):
                e = DLabSetupException("{}: '{}'".format(
                    e.strerror,
                    e.filename
                ))
            raise e

    def set_packages(self):
        """
        Set list of all Python import packages that should be included in the
        distribution package. Instead of listing each package manually, we can
        use find_packages() to automatically discover all packages and
        subpackages. In this case, the list of packages will be example_pkg as
        that's the only package present.

        :return: None
        """
        self._parameters['packages'] = find_packages()

    def set_requirements(self):
        content = self._read_file(REQUIREMENTS_FILE)
        self._parameters['install_requires'] = content.splitlines()

        if sys.platform == 'win32':
            self._parameters['install_requires'].append('pypiwin32')

    @property
    def lib_file(self):
        return self._name + '.py'

    @property
    def version_file(self):
        return os.path.join(self._name, VERSION_FILE)

    def set_version(self):
        """
        Set package version see PEP 440 for more details on versions

        :return: None
        """

        _locals = {}
        content = None

        if os.path.isfile(self.lib_file):
            content = self._read_file(self.lib_file)

        if content is None and os.path.isfile(self.version_file):
            content = self._read_file(self.version_file)

        if content is None:
            raise DLabSetupException('No version or library file')

        try:
            exec(content, None, _locals)
        except SyntaxError as e:
            raise DLabSetupException(e.text)

        try:
            self._parameters['version'] = _locals['__version__']
        except KeyError:
            raise DLabSetupException("name '{}' is not defined".format(
                '__version__'
            ))

    def set_long_description(self):
        """
        SET detailed description of the package. This is shown on the package
        detail package on the Python Package Index. In this case, the long
        description is loaded from README.md which is a common pattern.

        :return: None
        """

        content = self._read_file(README_FILE)
        self._parameters['long_description'] = content

    def set_entry_points(self):
        """
        A dictionary mapping entry point group names to strings or lists of
        strings defining the entry points. Entry points are used to support
        dynamic discovery of services or plugins provided by a project. See
        Dynamic Discovery of Services and Plugins for details and examples of
        the format of this argument. In addition, this keyword is used to
        support Automatic Script Creation.

        :return: None
        """
        self._parameters['entry_points'] = {}
