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
from itertools import groupby

from dlab_aws.infrastructure.controllers.deployment import AWSCLIController
from dlab_core.args_parser import ArgumentsBuilder

COMPONENT_SSN = 'ssn'
COMPONENT_ENDPOINT = 'endpoint'

ACTION_DEPLOY = 'deploy'
ACTION_DESTROY = 'destroy'

DEPLOY_ROUTES = [{
    'func': lambda: AWSCLIController.deploy_ssn(SSN_ARGUMENTS),
    'args': [None, COMPONENT_SSN, ACTION_DEPLOY]
}, {
    'func': lambda: AWSCLIController.destroy_ssn(SSN_ARGUMENTS),
    'args': [None, COMPONENT_SSN, ACTION_DESTROY]
}, {
    'func': lambda: AWSCLIController.deploy_endpoint(
        get_args(SSN_ARGUMENTS, ENDPOINT_ARGUMENTS)),
    'args': [None, COMPONENT_ENDPOINT, ACTION_DEPLOY]
}, {
    'func': AWSCLIController.destroy_endpoint,
    'args': [None, COMPONENT_ENDPOINT, ACTION_DESTROY]
}]


def get_args(args1, args2):
    sorted_args = sorted(args1 + args2, key=lambda x: x['key'])
    return [list(group)[0] for key, group
            in groupby(sorted_args, lambda x: x['key'])]


# TODO: move into plugin ini file package_data

"""SSN arguments (k8s, helm charts)"""
SSN_ARGUMENTS = ArgumentsBuilder().add(
    '--state', str, 'Path to state file').add(
    '--access_key_id', str, 'AWS Access Key ID', required=True).add(
    '--allowed_cidrs', str, 'CIDR to allow acces to SSN K8S cluster.',
    ["0.0.0.0/0"], action='append').add(
    '--ami', str, 'ID of EC2 AMI.', required=True).add(
    '--env_os', str, 'OS type.', 'debian', choices=['debian', 'redhat']).add(
    '--key_name', str, 'Name of EC2 Key pair.', required=True).add(
    '--os_user', str, 'Name of DLab service user.', 'dlab-user').add(
    '--region', str, 'Name of AWS region.', 'us-west-2').add(
    '--secret_access_key', str, 'AWS Secret Access Key', required=True).add(
    '--service_base_name', str,
    'Any infrastructure value (should be unique if multiple SSN\'s have been '
    'deployed before).', 'k8s').add(
    '--ssn_k8s_masters_count', int, 'Count of K8S masters.', 3).add(
    '--ssn_k8s_workers_count', int, 'Count of K8S workers', 2).add(
    '--ssn_k8s_masters_shape', str, 'Shape for SSN K8S masters.',
    't2.medium').add(
    '--ssn_k8s_workers_shape', str, 'Shape for SSN K8S workers.',
    't2.medium').add(
    '--subnet_cidr_a', str,
    'CIDR for Subnet creation in zone a. Conflicts with subnet_id'
    '_a.', '172.31.0.0/24').add(
    '--subnet_cidr_b', str,
    'CIDR for Subnet creation in zone b. Conflicts with subnet_id_b.',
    '172.31.1.0/24').add(
    '--subnet_cidr_c', str,
    'CIDR for Subnet creation in zone c. Conflicts with subnet_id_c.',
    '172.31.2.0/24').add(
    '--subnet_id_a', str,
    'ID of AWS Subnet in zone a if you already have subnet created.').add(
    '--subnet_id_b', str,
    'ID of AWS Subnet in zone b if you already have subnet created.').add(
    '--subnet_id_c', str,
    'ID of AWS Subnet in zone c if you already have subnet created.').add(
    '--vpc_cidr', str, 'CIDR for VPC creation. Conflicts with vpc_id',
    '172.31.0.0/16').add(
    '--vpc_id', str, 'ID of AWS VPC if you already have VPC created.').add(
    '--zone', str, 'Name of AWS zone', 'a').add(
    '--tag_resource_id', str, 'Tag resource ID.', 'user:tag').add(
    '--additional_tag', str, 'Additional tag.', 'product:dlab').add(
    '--ssn_root_volume_size', int, 'Size of root volume in GB.', 30).add(
    '--ssn_keystore_password', str, 'ssn_keystore_password').add(
    '--endpoint_keystore_password', str, 'endpoint_keystore_password').add(
    '--ssn_bucket_name', str, 'ssn_bucket_name').add(
    '--endpoint_eip_address', str, 'endpoint_eip_address').add(
    '--ldap_host', str, 'ldap host', required=True).add(
    '--ldap_dn', str, 'ldap dn', required=True).add(
    '--ldap_user', str, 'ldap user', required=True).add(
    '--ldap_bind_creds', str, 'ldap bind creds', required=True).add(
    '--ldap_users_group', str, 'ldap users group', required=True).add(
    '--ssn_subnet', str, 'ssn subnet id').add(
    '--ssn_k8s_sg_id', str, 'ssn sg ids').add(
    '--ssn_vpc_id', str, 'ssn vpc id').add(
    '--billing_bucket', str, 'Billing bucket name').add(
    '--billing_bucket_path', str,
    'The path to billing reports directory in S3 bucket', '').add(
    '--billing_aws_job_enabled', str,
    'Billing format. Available options: true (aws), false(epam)', 'false').add(
    '--billing_aws_account_id', str, 'The ID of Amazon account', '').add(
    '--billing_dlab_id', str,
    'Column name in report file that contains dlab id tag',
    'resource_tags_user_user_tag').add(
    '--billing_usage_date', str,
    'Column name in report file that contains usage date tag',
    'line_item_usage_start_date').add(
    '--billing_product', str,
    'Column name in report file that contains product name tag',
    'product_product_name').add(
    '--billing_usage_type', str,
    'Column name in report file that contains usage type tag',
    'line_item_usage_type').add(
    '--billing_usage', str,
    'Column name in report file that contains usage tag',
    'line_item_usage_amount').add(
    '--billing_cost', str, 'Column name in report file that contains cost tag',
    'line_item_blended_cost').add(
    '--billing_resource_id', str,
    'Column name in report file that contains dlab resource id tag',
    'line_item_resource_id').add(
    '--billing_tags', str, 'Column name in report file that contains tags',
    'line_item_operation,line_item_line_item_description').add(
    '--billing_tag', str, 'Billing tag', 'dlab').add(
    '--pkey', str, 'Path to key', required=True).add(
    '--no_color', bool, 'No color console output', True).build()

"""SSN arguments (k8s, helm charts)"""
ENDPOINT_ARGUMENTS = ArgumentsBuilder().add(
    '--no_color', bool, 'No color console output', True).add(
    '--state', str, 'State file path').add(
    '--secret_access_key', str, 'AWS Secret Access Key', required=True).add(
    '--access_key_id', str, 'AWS Access Key ID', required=True).add(
    '--pkey', str, 'path to key', required=True).add(
    '--service_base_name', str,
    'Any infrastructure value (should be unique if  multiple SSN\'s have '
    'been deployed before). Should be same as on ssn').add(
    '--vpc_id', str, 'ID of AWS VPC if you already have VPC created.').add(
    '--vpc_cidr', str, 'CIDR for VPC creation. Conflicts with vpc_id.',
    '172.31.0.0/16').add(
    '--ssn_subnet', str,
    'ID of AWS Subnet if you already have subnet created.').add(
    '--ssn_k8s_sg_id', str, 'ID of SSN SG.').add(
    '--subnet_cidr', str,
    'CIDR for Subnet creation. Conflicts with subnet_id.',
    '172.31.0.0/24').add(
    '--ami', str, 'ID of EC2 AMI.', required=True).add(
    '--key_name', str, 'Name of EC2 Key pair.', required=True).add(
    '--endpoint_id', str, 'Endpoint id.', required=True).add(
    '--region', str, 'Name of AWS region.', 'us-west-2').add(
    '--zone', str, 'Name of AWS zone.', 'a').add(
    '--network_type', str,
    'Type of created network (if network is not existed and require creation) '
    'for endpoint', 'public').add(
    '--endpoint_instance_shape', str, 'Instance shape of Endpoint.',
    't2.medium').add(
    '--endpoint_volume_size', int, 'Size of root volume in GB.', 30).add(
    '--endpoint_eip_allocation_id', str,
    'Elastic Ip created for Endpoint').add(
    '--product', str, 'Product name.', 'dlab').add(
    '--additional_tag', str, 'Additional tag.', 'product:dlab').add(
    '--ldap_host', str, 'ldap host', required=True).add(
    '--ldap_dn', str, 'ldap dn', required=True).add(
    '--ldap_user', str, 'ldap user', required=True).add(
    '--ldap_bind_creds', str, 'ldap bind creds', required=True).add(
    '--ldap_users_group', str, 'ldap users group', required=True).add(
    '--dlab_path', str, 'Dlab path', '/opt/dlab').add(
    '--key_name', str, 'Key name', '').add(
    '--endpoint_eip_address', str, 'Endpoint eip address').add(
    '--pkey', str, 'Pkey', '').add(
    '--hostname', str, 'Hostname', '').add(
    '--os_user', str, 'Os user', 'dlab-user').add(
    '--cloud_provider', str, 'Cloud provider', '').add(
    '--mongo_host', str, 'Mongo host', 'MONGO_HOST').add(
    '--mongo_port', str, 'Mongo port', '27017').add(
    '--ss_host', str, 'Ss host', '').add(
    '--ss_port', str, 'Ss port', '8443').add(
    '--keycloack_host', str, 'Keycloack host', '').add(
    '--repository_address', str, 'Repository address', '').add(
    '--repository_port', str, 'Repository port', '').add(
    '--repository_user', str, 'Repository user', '').add(
    '--repository_pass', str, 'Repository pass', '').add(
    '--docker_version', str, 'Docker version', '18.06.3~ce~3-0~ubuntu').add(
    '--ssn_bucket_name', str, 'Ssn bucket name', '').add(
    '--endpoint_keystore_password', str, 'Endpoint keystore password', '').add(
    '--keycloak_client_secret', str, 'Keycloak client secret', '').add(
    '--branch_name', str, 'Branch name', 'DLAB-terraform').add(
    '--env_os', str, 'Env os', 'debian').add(
    '--service_base_name', str, 'Service base name', '').add(
    '--edge_instence_size', str, 'Edge instence size', 't2.medium').add(
    '--subnet_id', str, 'Subnet id', '').add(
    '--region', str, 'Region', '').add(
    '--tag_resource_id', str, 'Tag resource id', 'user:tag').add(
    '--ssn_k8s_sg_id', str, 'Ssn k8s sg id', '').add(
    '--ssn_instance_size', str, 'Ssn instance size', 't2.large').add(
    '--vpc2_id', str, 'Vpc2 id', '').add(
    '--subnet2_id', str, 'Subnet2 id', '').add(
    '--conf_key_dir', str, 'Conf key dir', '/root/keys/').add(
    '--vpc_id', str, 'Vpc id', '').add(
    '--peering_id', str, 'Peering id', '').add(
    '--azure_resource_group_name', str, 'Azure resource group name', '').add(
    '--azure_ssn_storage_account_tag', str, 'Azure ssn storage account tag',
    '').add(
    '--azure_shared_storage_account_tag', str,
    'Azure shared storage account tag', '').add(
    '--azure_datalake_tag', str, 'Azure datalake tag', '').add(
    '--azure_client_id', str, 'Azure client id', '').add(
    '--gcp_project_id', str, 'Gcp project id', '').add(
    '--ldap_host', str, 'Ldap host', '').add(
    '--ldap_dn', str, 'Ldap dn', '').add(
    '--ldap_users_group', str, 'Ldap users group', '').add(
    '--ldap_user', str, 'Ldap user', '').add(
    '--ldap_bind_creds', str, 'Ldap bind creds', '').add(
    '--ssn_k8s_nlb_dns_name', str, 'Ssn k8s nlb dns name', '').add(
    '--ssn_k8s_alb_dns_name', str, 'Ssn k8s alb dns name', '').build()
