[![Maintainability](https://api.codeclimate.com/v1/badges/2270e9542f8d3ce871a5/maintainability)](https://codeclimate.com/github/mediapills/dlab/maintainability)
[![Coverage Status](https://codecov.io/gh/mediapills/dlab/branch/master/graph/badge.svg)](https://codecov.io/gh/mediapills/dlab)
[![Build Status](https://travis-ci.com/mediapills/dlab.svg?branch=master)](https://travis-ci.com/mediapills/dlab)
[![Documentation Status](https://readthedocs.org/projects/dlab/badge/?version=latest)](https://dlab.readthedocs.io/en/latest)
[![Requirements Status](https://requires.io/github/mediapills/dlab/requirements.svg?branch=master)](https://requires.io/github/mediapills/dlab/requirements/?branch=master)
[![License](http://img.shields.io/:license-Apache%202-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.txt)

Self-service, Fail-safe Exploratory Environment for Collaborative Data Science
Workflow

### Folder Structure Conventions

Folder structure options and naming conventions for software projects

**Directory layout :**

    .
    ├── dlab_core             # * dlab_core package source files
    │ ├── domain              # dlab_core package domain implementation
    │ ├── infrastructure      # dlab_core package infrastructure implementation
    │ ├── __init__.py         # define bound to names in the package namespace
    │ ├── __version__.py      # define version of current distributive
    │ └── setup.py            # helper for setuptools
    ├── plugins               # * dlab_core infrastructure plugins
    │ ├── dlab_deployment     # dlab_deployment package
    │ ├── dlab_aws            # package represent AWS cloud infrastructure
    │ ├── dlab_azure          # package represent Azure cloud infrastructure
    │ ├── dlab_gcp            # package represent GCP cloud infrastructure
    │ └── ...                 # ...
    ├── tests                 # Unit tests
    ├── LICENSE                 
    ├── README.md               
    ├── requirements.txt      # lists of production environment packages
    ├── requirements-dev.txt  # lists of development environment packages
    ├── setup.py              # describe dlab_core module distribution
    └── tox.ini               # automate  project testing in Python
