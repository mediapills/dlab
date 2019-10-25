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

from dlab_core.args_parser import ArgumentsBuilder


"""SSN arguments (k8s, helm charts)"""
SSN_ARGUMENTS = ArgumentsBuilder().add(
    '--state', type=str, help='Path to state file').add(
    '--access_key_id', type=str, help='AWS Access Key ID', required=True).add(
    '--allowed_cidrs', type=str,
    help='CIDR to allow acces to SSN K8S cluster.',
    default=["0.0.0.0/0"], action='append').add(
    '--ami', type=str, help='ID of EC2 AMI.', required=True).add(
    '--env_os', type=str, help='OS type.', default='debian',
    choices=['debian', 'redhat']).add(
    '--key_name', type=str, help='Name of EC2 Key pair.', required=True).add(
    '--os_user', type=str, help='Name of DLab service user.',
    default='dlab-user').add(
    '--region', type=str, help='Name of AWS region.', default='us-west-2').add(
    '--secret_access_key', type=str, help='AWS Secret Access Key',
    required=True).add(
    '--service_base_name', type=str,
    help='Any infrastructure value (should be unique if multiple SSN\'s '
         'have been deployed before).', default='k8s').add(
    '--ssn_k8s_masters_count', type=int, help='Count of K8S masters.',
    default=3).add(
    '--ssn_k8s_workers_count', type=int, help='Count of K8S workers',
    default=2).add(
    '--ssn_k8s_masters_shape', type=str, help='Shape for SSN K8S masters.',
    default='t2.medium').add(
    '--ssn_k8s_workers_shape', type=str, help='Shape for SSN K8S workers.',
    default='t2.medium').add(
    '--subnet_cidr_a', type=str,
    help='CIDR for Subnet creation in zone a. Conflicts with subnet_id_a.',
    default='172.31.0.0/24').add(
    '--subnet_cidr_b', type=str,
    help='CIDR for Subnet creation in zone b. Conflicts with subnet_id_b.',
    default='172.31.1.0/24').add(
    '--subnet_cidr_c', type=str,
    help='CIDR for Subnet creation in zone c. Conflicts with subnet_id_c.',
    default='172.31.2.0/24').add(
    '--subnet_id_a', type=str,
    help='ID of AWS Subnet in zone a if you already have subnet created.').add(
    '--subnet_id_b', type=str,
    help='ID of AWS Subnet in zone b if you already have subnet created.').add(
    '--subnet_id_c', type=str,
    help='ID of AWS Subnet in zone c if you already have subnet created.').add(
    '--vpc_cidr', type=str,
    help='CIDR for VPC creation. Conflicts with vpc_id',
    default='172.31.0.0/16').add(
    '--vpc_id', type=str,
    help='ID of AWS VPC if you already have VPC created.').add(
    '--zone', type=str, help='Name of AWS zone', default='a').add(
    '--tag_resource_id', type=str, help='Tag resource ID.',
    default='user:tag').add(
    '--additional_tag', type=str, help='Additional tag.',
    default='product:dlab').add(
    '--ssn_root_volume_size', type=int, help='Size of root volume in GB.',
    default=30).add(
    '--ssn_keystore_password', type=str, help='ssn_keystore_password').add(
    '--endpoint_keystore_password', type=str,
    help='endpoint_keystore_password').add(
    '--ssn_bucket_name', type=str, help='ssn_bucket_name').add(
    '--endpoint_eip_address', type=str, help='endpoint_eip_address').add(
    '--ldap_host', type=str, help='ldap host', required=True).add(
    '--ldap_dn', type=str, help='ldap dn', required=True).add(
    '--ldap_user', type=str, help='ldap user', required=True).add(
    '--ldap_bind_creds', type=str, help='ldap bind creds', required=True).add(
    '--ldap_users_group', type=str, help='ldap users group',
    required=True).add(
    '--ssn_subnet', type=str, help='ssn subnet id').add(
    '--ssn_k8s_sg_id', type=str, help='ssn sg ids').add(
    '--ssn_vpc_id', type=str, help='ssn vpc id').add(
    '--billing_bucket', type=str, help='Billing bucket name').add(
    '--billing_bucket_path', type=str,
    help='The path to billing reports directory in S3 bucket', default='').add(
    '--billing_aws_job_enabled', type=str,
    help='Billing format. Available options: true (aws), false(epam)',
    default='false').add(
    '--billing_aws_account_id', type=str, help='The ID of Amazon account',
    default='').add(
    '--billing_dlab_id', type=str,
    help='Column name in report file that contains dlab id tag',
    default='resource_tags_user_user_tag').add(
    '--billing_usage_date', type=str,
    help='Column name in report file that contains usage date tag',
    default='line_item_usage_start_date').add(
    '--billing_product', type=str,
    help='Column name in report file that contains product name tag',
    default='product_product_name').add(
    '--billing_usage_type', type=str,
    help='Column name in report file that contains usage type tag',
    default='line_item_usage_type').add(
    '--billing_usage', type=str,
    help='Column name in report file that contains usage tag',
    default='line_item_usage_amount').add(
    '--billing_cost', type=str,
    help='Column name in report file that contains cost tag',
    default='line_item_blended_cost').add(
    '--billing_resource_id', type=str,
    help='Column name in report file that contains dlab resource id tag',
    default='line_item_resource_id').add(
    '--billing_tags', type=str,
    help='Column name in report file that contains tags',
    default='line_item_operation,line_item_line_item_description').add(
    '--billing_tag', type=str, help='Billing tag', default='dlab').add(
    '--pkey', type=str, help='Path to key', required=True).add(
    '--no_color', type=bool, help='No color console output',
    default=True).build()

"""SSN arguments (k8s, helm charts)"""
ENDPOINT_ARGUMENTS = ArgumentsBuilder().add(
    '--no_color', type=bool, help='No color console output', default=True).add(
    '--state', type=str, help='State file path').add(
    '--secret_access_key', type=str, help='AWS Secret Access Key',
    required=True).add(
    '--access_key_id', type=str, help='AWS Access Key ID', required=True).add(
    '--pkey', type=str, help='path to key', required=True).add(
    '--service_base_name', type=str,
    help='Any infrastructure value (should be unique if  multiple SSN\'s have '
         'been deployed before). Should be same as on ssn').add(
    '--vpc_id', type=str,
    help='ID of AWS VPC if you already have VPC created.').add(
    '--vpc_cidr', type=str,
    help='CIDR for VPC creation. Conflicts with vpc_id.',
    default='172.31.0.0/16').add(
    '--ssn_subnet', type=str,
    help='ID of AWS Subnet if you already have subnet created.').add(
    '--ssn_k8s_sg_id', type=str, help='ID of SSN SG.').add(
    '--subnet_cidr', type=str,
    help='CIDR for Subnet creation. Conflicts with subnet_id.',
    default='172.31.0.0/24').add(
    '--ami', type=str, help='ID of EC2 AMI.', required=True).add(
    '--key_name', type=str, help='Name of EC2 Key pair.', required=True).add(
    '--endpoint_id', type=str, help='Endpoint id.', required=True).add(
    '--region', type=str, help='Name of AWS region.', default='us-west-2').add(
    '--zone', type=str, help='Name of AWS zone.', default='a').add(
    '--network_type', type=str,
    help='Type of created network '
         '(if network is not existed and require creation) for endpoint',
    default='public').add(
    '--endpoint_instance_shape', type=str, help='Instance shape of Endpoint.',
    default='t2.medium').add(
    '--endpoint_volume_size', type=int, help='Size of root volume in GB.',
    default=30).add(
    '--endpoint_eip_allocation_id', type=str,
    help='Elastic Ip created for Endpoint').add(
    '--product', type=str, help='Product name.', default='dlab').add(
    '--additional_tag', type=str, help='Additional tag.',
    default='product:dlab').add(
    '--ldap_host', type=str, help='ldap host', required=True).add(
    '--ldap_dn', type=str, help='ldap dn', required=True).add(
    '--ldap_user', type=str, help='ldap user', required=True).add(
    '--ldap_bind_creds', type=str, help='ldap bind creds', required=True).add(
    '--ldap_users_group', type=str, help='ldap users group',
    required=True).add(
    '--dlab_path', type=str, help='Dlab path', default='/opt/dlab').add(
    '--key_name', type=str, help='Key name', default='').add(
    '--endpoint_eip_address', type=str, help='Endpoint eip address').add(
    '--pkey', type=str, help='Pkey', default='').add(
    '--hostname', type=str, help='Hostname', default='').add(
    '--os_user', type=str, help='Os user', default='dlab-user').add(
    '--cloud_provider', type=str, help='Cloud provider', default='').add(
    '--mongo_host', type=str, help='Mongo host', default='MONGO_HOST').add(
    '--mongo_port', type=str, help='Mongo port', default='27017').add(
    '--ss_host', type=str, help='Ss host', default='').add(
    '--ss_port', type=str, help='Ss port', default='8443').add(
    '--keycloack_host', type=str, help='Keycloack host', default='').add(
    '--repository_address', type=str, help='Repository address',
    default='').add(
    '--repository_port', type=str, help='Repository port', default='').add(
    '--repository_user', type=str, help='Repository user', default='').add(
    '--repository_pass', type=str, help='Repository pass', default='').add(
    '--docker_version', type=str, help='Docker version',
    default='18.06.3~ce~3-0~ubuntu').add(
    '--ssn_bucket_name', type=str, help='Ssn bucket name', default='').add(
    '--endpoint_keystore_password', type=str,
    help='Endpoint keystore password', default='').add(
    '--keycloak_client_id', type=str, help='Keycloak client id',
    default='').add(
    '--keycloak_client_secret', type=str, help='Keycloak client secret',
    default='').add(
    '--mongo_password', type=str, help='Mongo password', default='').add(
    '--branch_name', type=str, help='Branch name',
    default='DLAB-terraform').add(
    '--env_os', type=str, help='Env os', default='debian').add(
    '--service_base_name', type=str, help='Service base name', default='').add(
    '--edge_instence_size', type=str, help='Edge instence size',
    default='t2.medium').add(
    '--subnet_id', type=str, help='Subnet id', default='').add(
    '--region', type=str, help='Region', default='').add(
    '--tag_resource_id', type=str, help='Tag resource id',
    default='user:tag').add(
    '--ssn_k8s_sg_id', type=str, help='Ssn k8s sg id', default='').add(
    '--ssn_instance_size', type=str, help='Ssn instance size',
    default='t2.large').add(
    '--vpc2_id', type=str, help='Vpc2 id', default='').add(
    '--subnet2_id', type=str, help='Subnet2 id', default='').add(
    '--conf_key_dir', type=str, help='Conf key dir',
    default='/root/keys/').add(
    '--vpc_id', type=str, help='Vpc id', default='').add(
    '--peering_id', type=str, help='Peering id', default='').add(
    '--azure_resource_group_name', type=str, help='Azure resource group name',
    default='').add(
    '--azure_ssn_storage_account_tag', type=str,
    help='Azure ssn storage account tag',
    default='').add(
    '--azure_shared_storage_account_tag', type=str,
    help='Azure shared storage account tag', default='').add(
    '--azure_datalake_tag', type=str, help='Azure datalake tag',
    default='').add(
    '--azure_client_id', type=str, help='Azure client id', default='').add(
    '--gcp_project_id', type=str, help='Gcp project id', default='').add(
    '--ldap_host', type=str, help='Ldap host', default='').add(
    '--ldap_dn', type=str, help='Ldap dn', default='').add(
    '--ldap_users_group', type=str, help='Ldap users group', default='').add(
    '--ldap_user', type=str, help='Ldap user', default='').add(
    '--ldap_bind_creds', type=str, help='Ldap bind creds', default='').add(
    '--ssn_k8s_nlb_dns_name', type=str, help='Ssn k8s nlb dns name',
    default='').add(
    '--ssn_k8s_alb_dns_name', type=str, help='Ssn k8s alb dns name',
    default='').build()

PROJECT_ARGUMENTS = ArgumentsBuilder().add(
    '--access_key_id', type=str, help='Access secret key', required=True).add(
    '--secret_access_key', type=str, help='Secret access key',
    required=True).add(
    '--service_base_name', type=str, help='Service base name',
    required=True).add(
    '--project_name', type=str, help='Project name', required=True).add(
    '--project_tag', type=str, help='Project tag', required=True).add(
    '--endpoint_tag', type=str, help='Endpoint tag', required=True).add(
    '--user_tag', type=str, help='User tag', required=True).add(
    '--custom_tag', type=str, help='Custom tag', required=True).add(
    '--region', type=str, help='Region', required=True).add(
    '--zone', type=str, help='Zone', required=True).add(
    '--vpc_id', type=str, help='VPC id', required=True).add(
    '--subnet_id', type=str, help='Subnet id', required=True).add(
    '--nb_cidr', type=str, help='NB cidr', required=True).add(
    '--edge_cidr', type=str, help='EDGE cidr', required=True).add(
    '--ami', type=str, help='AMI', required=True).add(
    '--instance_type', type=str, help='Instance type', required=True).add(
    '--key_name', type=str, help='Key name', required=True).add(
    '--edge_volume_size', type=str, help='Edge_volume size',
    required=True).add(
    '--additional_tag', type=str, help='Additional tag',
    default='product:dlab').add(
    '--tag_resource_id', type=str, help='Tag resource id',
    default='user:tag').build()
