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


"""Author of the package email address"""
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


class SetupException(Exception):
    """Class for Setup exceptions."""
    pass


class FileNotFoundException(IOError):
    """Exception class thrown when a file couldn't be found"""
    pass


@six.add_metaclass(abc.ABCMeta)
class BaseSetupParametersBuilder:
    """Abstract interface for creating setup parameters"""

    @abc.abstractmethod
    def set_packages(self):
        """Set list of all Python import packages that should be included in
        the distribution package. Instead of listing each package manually, we
        can use find_packages() to automatically discover all packages and
        subpackages. In this case, the list of packages will be example_pkg as
        that's the only package present.

        :return: None
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_requirements(self):
        """Set libraries list that should be used to specify what a project
        minimally needs to run correctly. When the project is installed by pip,
        this is the specification that is used to install its dependencies.

        :return: None
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_version(self):
        """Set package version see PEP 440 for more details on versions.

        :return: None
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_long_description(self):
        """Set detailed description of the package. This is shown on the
        package detail package on the Python Package Index. In this case, the
        long description is loaded from README.md which is a common pattern.

        :return: None
        """

        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parameters(self):
        """Get parameters list as dict for setup.py

        :return: dict
        """

        raise NotImplementedError


class SetupParametersDirector:
    """Construct an parameters dict using the BaseSetupParametersBuilder
    interface.
    """

    def __init__(self):
        """Director constructor.
        """
        self._builder = None

    def build(self, builder):
        """Build setup parameters.

        :param builder: Parameters builder.
        :type builder: BaseSetupParametersBuilder

        :return: None
        """
        self._builder = builder

        self._builder.set_packages()
        self._builder.set_requirements()
        self._builder.set_version()
        self._builder.set_long_description()

    @property
    def parameters(self):
        """Get parameters list as dict for setup.py

        :return: dict
        """

        builder = self._builder  # type: BaseSetupParametersBuilder
        return builder.parameters


class SetupParametersBuilder(BaseSetupParametersBuilder):
    """Creating parts of a setup parameters dict see PEP 561 for more details
    about Distributing and Packaging Type Information
    """

    def __init__(self, name, description):
        """Builder constructor.

        :type name: str
        :param name: Distribution name of your package.

        :type description: str
        :param description: Short, one-sentence summary of the package.
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
            'long_description_content_type': DESCRIPTION_CONTENT_TYPE,
            'packages': None,
            'install_requires': None,
            'version': None,
            'long_description': None,
        }

    @property
    def parameters(self):
        """Get parameters list as dict for setup.py

        :return: dict
        """
        return self._parameters

    @staticmethod
    def _read_file(name):
        """Get content by filename.

        :type name: str
        :param name: File location.

        :return: str
        """

        if not os.path.isfile(name):
            raise FileNotFoundException(
                "No such file or directory: '{}'".format(name)
            )

        try:
            with open(name, "r") as fh:
                return fh.read()
        except IOError as e:
            if hasattr(e, 'filename'):
                e = SetupException("{}: '{}'".format(
                    e.strerror,
                    e.filename
                ))
            raise e

    def set_packages(self):
        """Set list of all Python import packages that should be included in
        the distribution package. Instead of listing each package manually, we
        can use find_packages() to automatically discover all packages and
        subpackages. In this case, the list of packages will be example_pkg as
        that's the only package present.

        :return: None
        """

        self._parameters['packages'] = find_packages()

    def set_requirements(self):
        """Set libraries list that should be used to specify what a project
        minimally needs to run correctly. When the project is installed by pip,
        this is the specification that is used to install its dependencies.

        :return: None
        """

        content = self._read_file(REQUIREMENTS_FILE)
        self._parameters['install_requires'] = content.splitlines()

        if sys.platform == 'win32':
            self._parameters['install_requires'].append('pypiwin32')

    @property
    def lib_file(self):
        """Get library file location.

        :return: str
        """
        return self._name + '.py'

    @property
    def version_file(self):
        """Get version file location.

        :return: str
        """
        return os.path.join(self._name, VERSION_FILE)

    def set_version(self):
        """Set package version see PEP 440 for more details on versions.

        :return: None
        """

        _locals = {}

        try:
            content = self._read_file(self.lib_file)
        except FileNotFoundException:
            content = None

        try:
            if content is None:
                content = self._read_file(self.version_file)
            exec(content, None, _locals)
            self._parameters['version'] = _locals['__version__']
        except SyntaxError as e:
            raise SetupException(e.text)
        except KeyError:
            raise SetupException("name '{}' is not defined".format(
                '__version__'
            ))
        except FileNotFoundException:
            raise SetupException('No version or library file')

    def set_long_description(self):
        """Set detailed description of the package. This is shown on the
        package detail package on the Python Package Index. In this case, the
        long description is loaded from README.md which is a common pattern.

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
        raise NotImplementedError
