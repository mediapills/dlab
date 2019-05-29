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
import sys
from setuptools import setup, find_packages

__version_info__ = (0, 0, 1)
__version__ = ".".join(map(str, __version_info__))

NAME = "dlab"
DESCRIPTION = "DLab CLI - Common functionality"
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
URL = "https://github.com/apache/incubator-dlab"
AUTHOR = "Andrew Yatskovets"
AUTHOR_EMAIL = 'andrew.yatskovets@gmail.com'

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

packages = find_packages()

requirements = [
    'six',
    'configparser',
    'flask'
]
# TODO: while tox create environment it can't read from local file
# TODO: need to be clarified
# with open('requirements.txt') as f:
#     requirements = f.read().splitlines()

if sys.platform == 'win32':
    requirements.append('pypiwin32')

# TODO: while tox create environment it can't read from local file
# TODO: need to be clarified

# Version info -- read without importing
# _locals = {}
# with open("version.py") as fp:
#     exec(fp.read(), None, _locals)
version = __version__

setup(
    name=NAME,
    version=version,
    description=DESCRIPTION,
    classifiers=CLASSIFIERS,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache-2.0",
    packages=packages,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=requirements,
    scripts=['bin/dlabcli'],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
)
