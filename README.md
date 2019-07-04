
[![Coverage Status](https://codecov.io/gh/mediapills/dlab/branch/master/graph/badge.svg)](https://codecov.io/gh/mediapills/dlab)
[![Documentation Status](https://readthedocs.org/projects/dlab/badge/?version=latest)](https://dlab.readthedocs.io/en/latest)
[![License](http://img.shields.io/:license-Apache%202-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.txt)
[![Build Status](https://travis-ci.com/mediapills/dlab.svg?branch=master)](https://travis-ci.com/mediapills/dlab)

Self-service, Fail-safe Exploratory Environment for Collaborative Data Science Workflow 

### Folder Structure Conventions

Folder structure options and naming conventions for software projects

**Directory layout :**

    .
    ├── dlab_core               # * dlab_core package source files
    │ ├── domain                # dlab_core package domain implementation 
    │ ├── infrastructure        # dlab_core package infrastructure implementation
    │ ├── __init__.py           # define bound to names in the dlab_core package namespace
    │ ├── __version__.py        # define version of current distributive 
    │ └── setup.py              # helper for setuptools
    ├── providers               # * dlab_core infrastructure providers
    │ ├── dlab_aws              # dlab_core package represent AWS cloud infrastructure managers
    │ ├── dlab_azure            # dlab_azure package represent Azure cloud infrastructure managers
    │ ├── dlab_gcp              # dlab_gcp package represent GCP cloud infrastructure managers
    │ └── ...                   # ...
    ├── tests                   # Unit tests
    ├── LICENSE                 
    ├── README.md               
    ├── requirements.txt        # lists of packages to install for dlab_core production environment
    ├── requirements-dev.txt    # lists of packages to install for dlab_core development environment
    ├── setup.py                # describe dlab_core module distribution to the Distutils
    └── tox.ini                 # automate and standardize project testing in Python 

### Branch Naming Conventions

```
{feature|fix|poc}/{package|provider|plugin name}/{section name}
```

**Example**

```
$ git branch
  feature/ci/travis
  feature/core/logger
  feature/doc/readme
  fix/core/setup
* master
```

**Available packages:**

| Name          | Description                 |
| ------------- | --------------------------- |
| aws           | dlab_aws package            |
| azure         | dlab_azure package          |
| ci            | ci/cd related files         |
| core          | dlab_core package           |
| doc           | documentation related files |
| gcp           | dlab_gcp package            |

**Available sections:**

| Name          | Description                 |
| ------------- | --------------------------- |
| controller    | controller changes          |
| license       | license information         |
| logger        | logger implementation       |
| readme        | readme information          |
| setup         | setup helper change         |
| travis        | travis related changes      |
| usecase       | use case changes            |

> TODO: synchronize sections with git labels

### PR Naming Conventions

**Example**

```
aws - infrastructure Create CloudWatch logger
```

The description should contain the following headings and the related content:

```
# What does this PR do?
# Description of Task to be completed?
# How should this be manually tested?
# Any background context you want to provide?
# What are the relevant pivotal tracker stories?
# Screenshots (if appropriate)
# Questions:
```

> NOTE: We expect to have one commit per pull request

> NOTE: After creation PR needs to be tagged regards branch namespace
