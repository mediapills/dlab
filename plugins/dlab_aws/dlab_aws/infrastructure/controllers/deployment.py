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
import os

from dlab_core.args_parser import CLIArgsParser
from dlab_deployment.domain.usecases import SSNProvisionUseCase, \
    SSNConfigurationUseCase, SSNDestroyUseCase
from dlab_deployment.infrastructure.command_executor import (
    LocalCommandExecutor, ParamikoCommandExecutor)
from dlab_deployment.infrastructure.controllers import (
    BaseDeploymentCLIController)
from dlab_deployment.infrastructure.service_providers import (
    TerraformServiceProvider)

SSN_TF_KEYS = [
    'access_key_id', 'allowed_cidrs', 'key_name', 'region', 'os_user',
    'ami', 'secret_access_key', 'service_base_name', 'ssn_k8s_masters_count',
    'ssn_k8s_workers_count', 'ssn_k8s_masters_shape', 'ssn_k8s_workers_shape',
    'ssn_root_volume_size', 'subnet_cidr_a', 'subnet_cidr_b', 'subnet_cidr_c',
    'subnet_id_a', 'subnet_id_b', 'subnet_id_c', 'vpc_cidr', 'vpc_id', 'zone',
    'tag_resource_id', 'additional_tag', 'env_os'
]

HELM_CHARTS_CHARTS_ARGS = [
    'env_os', 'region', 'service_base_name', 'ssn_k8s_workers_count',
    'ssn_k8s_masters_shape', 'zone', 'ssn_keystore_password',
    'endpoint_keystore_password', 'ssn_bucket_name', 'endpoint_eip_address',
    'ldap_host', 'ldap_dn', 'ldap_user', 'ldap_bind_creds', 'ldap_users_group',
    'ssn_subnet', 'ssn_k8s_sg_id', 'ssn_vpc_id', 'tag_resource_id',
    'billing_bucket', 'billing_bucket_path', 'billing_aws_job_enabled',
    'billing_aws_account_id', 'billing_dlab_id', 'billing_usage_date',
    'billing_product', 'billing_usage_type', 'billing_usage', 'billing_cost',
    'billing_resource_id', 'billing_tags', 'billing_tag'
]

STATE_TF_OPTION = 'state'
NO_COLOR_TF_OPTION = 'no_color'

SSN_TERRAFORM_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '../../terraform/ssn'))
HELM_CHARTS_TERRAFORM_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '../../terraform/helm_charts'))
HELM_CHARTS_REMOTE_TERRAFORM_PATH = 'helm_charts'
ENDPOINT_TERRAFORM_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '../../terraform/endpoint'))


class AWSController(BaseDeploymentCLIController):

    @staticmethod
    def init_terraform_provider(executor, path, arguments, keys):
        return TerraformServiceProvider(
            command_executor=executor,
            no_color=arguments.get(NO_COLOR_TF_OPTION),
            tf_path=path,
            state=arguments.get(STATE_TF_OPTION),
            variables={k: v for k, v in arguments.items() if k in keys}
        )

    @classmethod
    def deploy_ssn(cls, args):
        local_terraform_provider = cls.init_terraform_provider(
            LocalCommandExecutor(), SSN_TERRAFORM_PATH, args, SSN_TF_KEYS)
        ssn_provision_use_case = SSNProvisionUseCase(local_terraform_provider)
        ssn_provision_use_case.execute()
        output = local_terraform_provider.output()
        master_ip = output.get('ssn_k8s_masters_ip_addresses', [None])[0]
        user_name = args.get('os_user')
        key = args.get('pkey')
        args.update(output)
        paramiko_executor = ParamikoCommandExecutor(master_ip, user_name, key)
        remote_terraform_provider = cls.init_terraform_provider(
            paramiko_executor, HELM_CHARTS_REMOTE_TERRAFORM_PATH, args,
            HELM_CHARTS_CHARTS_ARGS)
        ssn_configuration_use_case = SSNConfigurationUseCase(
            remote_terraform_provider, paramiko_executor,
            HELM_CHARTS_TERRAFORM_PATH, HELM_CHARTS_REMOTE_TERRAFORM_PATH)
        ssn_configuration_use_case.execute()

    @classmethod
    def destroy_ssn(cls, args):
        local_terraform_provider = cls.init_terraform_provider(
            LocalCommandExecutor(), SSN_TERRAFORM_PATH, args, SSN_TF_KEYS)
        ssn_destroy_use_case = SSNDestroyUseCase(local_terraform_provider)
        ssn_destroy_use_case.execute()

    @classmethod
    def deploy_endpoint(cls):
        raise NotImplementedError

    @classmethod
    def destroy_endpoint(cls):
        raise NotImplementedError


class AWSCLIController(AWSController):

    @classmethod
    def deploy_ssn(cls, available_args):
        args = CLIArgsParser(available_args).parse_args()
        super(AWSCLIController, cls).deploy_ssn(args)

    @classmethod
    def destroy_ssn(cls, available_args):
        args = CLIArgsParser(available_args).parse_args()
        super(AWSCLIController, cls).destroy_ssn(args)

    @classmethod
    def deploy_endpoint(cls):
        raise NotImplementedError

    @classmethod
    def destroy_endpoint(cls):
        raise NotImplementedError
