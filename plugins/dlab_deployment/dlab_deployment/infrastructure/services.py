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


@six.add_metaclass(abc.ABCMeta)
class BaseDeploymentService(object):

    @abc.abstractmethod
    def deploy(self, iac_provider, source_provider):
        """
        :type iac_provider: BaseIACProvider
        :param iac_provider: Infrastructure as code provider
        :type source_provider: BaseSourceProvider
        :param source_provider: Source provider
        """
        pass

    @abc.abstractmethod
    def destroy(self, iac_provider, source_provider):
        """
        :type iac_provider: BaseIACProvider
        :param iac_provider: Infrastructure as code provider
        :type source_provider: BaseSourceProvider
        :param source_provider: Source provider
        """
        pass


class DeploymentService(BaseDeploymentService):

    @classmethod
    def deploy(cls, iac_provider, source_provider):
        """
        :type iac_provider: BaseIACProvider
        :param iac_provider: Infrastructure as code provider
        :type source_provider: BaseSourceProvider
        :param source_provider: Source provider
        """
        arguments = source_provider.parse_args()
        iac_provider.initialize()
        iac_provider.validate()
        iac_provider.apply(arguments)
        source_provider.deploy()

    @classmethod
    def destroy(cls, iac_provider, source_provider):
        """
        :type iac_provider: BaseIACProvider
        :param iac_provider: Infrastructure as code provider
        :type source_provider: BaseSourceProvider
        :param source_provider: Source provider
        """
        arguments = source_provider.parse_args()
        iac_provider.initialize()
        iac_provider.validate()
        iac_provider.destroy(arguments)
        source_provider.deploy()

