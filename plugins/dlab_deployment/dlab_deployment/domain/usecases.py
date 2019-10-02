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

from dlab_core.domain.helper import break_after
from dlab_core.domain.usecases import BaseUseCase, UseCaseException
from dlab_deployment.domain.service_providers import BaseIaCServiceProvider

LC_ERR_ILLEGAL_SERVICE_PROVIDER = (
    'Invalid service provider of type {}, should be instance of {}')

TIME_OUT = 300


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


class ConfigurationUseCase(BaseUseCase):
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


class SSNConfigurationUseCase(ConfigurationUseCase):

    def __init__(self, terraform_provider, command_executor,
                 helm_charts_location, helm_charts_remote_location):
        """
        :type terraform_provider: BaseIaCServiceProvider
        :param terraform_provider:  Terraform service provider
        :type command_executor: BaseCommandExecutor
        :param command_executor: remote cli
        :type helm_charts_location: str
        :param helm_charts_location: path to helm charts
        :type helm_charts_remote_location:
        :param helm_charts_remote_location: path for remote terraform
        """

        self.command_executor = command_executor
        self.terraform_provider = terraform_provider
        self.helm_charts_location = helm_charts_location
        self.helm_charts_remote_location = helm_charts_remote_location

    def execute(self):
        """Configure instance
        Check k8s and tiller status
        Copy helm charts to instance
        Provision helm charts
        """
        self.check_k8s_status()
        self.check_tiller_status()
        self.copy_terraform_to_remote()
        self.terraform_provider.provision()

    @break_after(TIME_OUT)
    def check_k8s_status(self):
        """ Check kubernetes status """
        command = ('kubectl cluster-info | '
                   r'sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g"')
        kubernetes_success_status = 'Kubernetes master is running'
        kubernetes_dns_success_status = 'KubeDNS is running'
        while True:
            k8c_info_status = self.command_executor.run(command)
            kubernetes_succeed = kubernetes_success_status in k8c_info_status
            kube_dns_succeed = kubernetes_dns_success_status in k8c_info_status
            if kubernetes_succeed and kube_dns_succeed:
                return

    @break_after(TIME_OUT)
    def check_tiller_status(self):
        """ Check tiller status """

        command = ('kubectl get pods --all-namespaces | '
                   'grep tiller | awk "{print $4}"')
        tiller_success_status = 'Running'
        while True:
            tiller_status = self.command_executor.run(command)
            if tiller_success_status in tiller_status:
                return

    def copy_terraform_to_remote(self):
        """Transfer helm charts terraform files"""
        self.command_executor.put(
            self.helm_charts_location, self.helm_charts_remote_location)


class EndpointProvisionUseCase(ProvisionUseCase):
    pass


class EndpointConfigurationUseCase(ConfigurationUseCase):
    def execute(self):
        raise NotImplementedError


class EndpointDestroyUseCase(DestroyUseCase):
    pass
