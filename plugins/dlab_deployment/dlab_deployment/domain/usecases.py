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
# *****************************************************************************

import abc

import six

from dlab_core.domain.usecases import BaseUseCase, UseCaseException
from dlab_deployment.domain.service_providers import BaseIaCServiceProvider

LC_ERR_ILLEGAL_SERVICE_PROVIDER = (
    'Invalid service provider of type {}, should be instance of {}')


def validate_service_provider_type(provider_type):
    """Validate passed to setter service provider type"""
    def validate_service_provider(fn):
        def wrapped(*args, **kwargs):
            service_provider = args[1]
            if not isinstance(service_provider, provider_type):
                raise UseCaseException(
                    LC_ERR_ILLEGAL_SERVICE_PROVIDER.format(
                        type(service_provider).__name__, provider_type.__name__
                    ))
            return fn(*args, **kwargs)
        return wrapped
    return validate_service_provider


@six.add_metaclass(abc.ABCMeta)
class DeploymentUseCase(BaseUseCase):
    def __init__(self, iac_service_provider):
        """
        :type iac_service_provider: BaseIaCServiceProvider
        :param iac_service_provider: Infrastructure as Code service provider
        """

        self.iac_service_provider = iac_service_provider

    @property
    def iac_service_provider(self):
        """
        :rtype: BaseIaCServiceProvider
        :return: Infrastructure as Code service provider
        """

        return self._iac_service_provider

    @iac_service_provider.setter
    @validate_service_provider_type(BaseIaCServiceProvider)
    def iac_service_provider(self, iac_service_provider):
        """
        :type: BaseIaCServiceProvider
        :param iac_service_provider: Infrastructure as Code service provider
        """

        self._iac_service_provider = iac_service_provider

    @abc.abstractmethod
    def execute(self):
        raise NotImplementedError


class ProvisionUseCase(DeploymentUseCase):

    def execute(self):
        """Provision infrastructure"""

        self.iac_service_provider.provision()


class DestroyUseCase(DeploymentUseCase):

    def execute(self):
        """Destroy infrastructure"""

        self.iac_service_provider.destroy()


class SSNProvisionUseCase(ProvisionUseCase):
    pass


class SSNDestroyUseCase(DestroyUseCase):
    pass


class EndpointProvisionUseCase(ProvisionUseCase):
    pass


class EndpointDestroyUseCase(DestroyUseCase):
    pass
