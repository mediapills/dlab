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
import sys
import time
import traceback

import six

from dlab_deployment.infrastructure.command_executor import \
    ParamikoCommandExecutor
from dlab_core.domain.helper import break_after
from dlab_core.domain.usecases import BaseUseCase, UseCaseException
from dlab_deployment.domain.service_providers import BaseIaCServiceProvider

LC_ERR_ILLEGAL_SERVICE_PROVIDER = (
    'Invalid service provider of type {}, should be instance of {}')
K8S_STATUS_COMMAND = r'kubectl cluster-info | ' \
                     r'sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g"'
TILLER_STATUS_COMMAND = 'kubectl get pods --all-namespaces | ' \
                        'grep tiller | awk "{print $4}"'
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
        kubernetes_success_status = 'Kubernetes master is running'
        kubernetes_dns_success_status = 'KubeDNS is running'
        while True:
            k8c_info_status = self.command_executor.run(K8S_STATUS_COMMAND)
            kubernetes_succeed = kubernetes_success_status in k8c_info_status
            kube_dns_succeed = kubernetes_dns_success_status in k8c_info_status
            if kubernetes_succeed and kube_dns_succeed:
                return
            time.sleep(10)

    @break_after(TIME_OUT)
    def check_tiller_status(self):
        """ Check tiller status """

        tiller_success_status = 'Running'
        while True:
            tiller_status = self.command_executor.run(TILLER_STATUS_COMMAND)
            if tiller_success_status in tiller_status:
                return
            time.sleep(10)

    def copy_terraform_to_remote(self):
        """Transfer helm charts terraform files"""
        self.command_executor.put(
            self.helm_charts_location, self.helm_charts_remote_location)


class EndpointProvisionUseCase(ProvisionUseCase):
    pass


class EndpointConfigurationUseCase(ConfigurationUseCase):

    def __init__(self, command_executor, cli_args):
        """
        :type command_executor: BaseCommandExecutor
        :param command_executor: remote cli
        """

        self.console = command_executor
        self.cli_args = cli_args
        self.java_home = None
        self.master_ip = cli_args['master_ip']

    def execute(self):
        time.sleep(40)

        # TEMPORARY!!!
        self.cli_args['keycloack_host'] = self.cli_args['ssn_k8s_alb_dns_name']
        self.cli_args['ss_host'] = self.cli_args['ssn_k8s_nlb_dns_name']
        # TEMPORARY!!!

        self.create_user()
        self.init_dlab_connection()
        self.update_system()
        self.ensure_dir_endpoint()
        self.ensure_logs_endpoint()
        self.ensure_jre_jdk_endpoint()
        self.set_java_home()
        self.ensure_supervisor_endpoint()
        self.ensure_docker_endpoint()
        self.configure_supervisor_endpoint()
        self.create_key_dir_endpoint()
        self.copy_keys()
        self.configure_keystore_endpoint(self.cli_args['os_user'])
        self.ensure_jar_endpoint()
        self.get_sources()
        self.pull_docker_images()
        self.start_supervisor_endpoint()

    def exists(self, path):
        return self.cli_args.run('test -e {} && exists'.format(path))

    def create_user(self):
        initial_user = 'ubuntu'
        sudo_group = 'sudo'
        os_user = self.cli_args.get('os_user')
        commands = [
            'useradd -m -G {1} -s /bin/bash {0}'.format(
                os_user, sudo_group),
            'bash -c \'echo "{} ALL = NOPASSWD:ALL" >> /etc/sudoers\''.format(
                os_user, initial_user),
            'mkdir /home/{}/.ssh'.format(os_user),
            'chown -R {0}:{0} /home/{1}/.ssh/'.format(initial_user, os_user),
            'cat /home/{0}/.ssh/authorized_keys > '
            '/home/{1}/.ssh/authorized_keys'.format(initial_user, os_user),
            'chown -R {0}:{0} /home/{0}/.ssh/'.format(os_user),
            'chmod 700 /home/{0}/.ssh'.format(os_user),
            'chmod 600 /home/{0}/.ssh/authorized_keys'.format(os_user),
            'touch /home/{}/.ssh_user_ensured'.format(initial_user),
        ]

        try:
            if not self.exists(
                    'home/{}/.ssh_user_ensured && exist'.format(initial_user)):
                for command in commands:
                    self.console.sudo(command)
        except Exception:
            sys.exit(1)

    def copy_keys(self):
        try:
            self.console.put(
                self.cli_args.get('pkey'),
                '/home/{0}/keys/'.format(self.cli_args.get('os_user')))
            self.console.sudo(
                'chown -R {0}:{0} /home/{0}/keys'.format(
                    self.cli_args.get('os_user')))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def ensure_dir_endpoint(self):
        os_user = self.cli_args.get('os_user')
        try:
            if not self.exists('/home/{}/.ensure_dir'.format(os_user)):
                self.console.sudo(
                    'mkdir /home/{}/.ensure_dir'.format(os_user))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def ensure_logs_endpoint(self):
        log_root_dir = "/var/opt/dlab/log"
        supervisor_log_file = "/var/log/application/provision-service.log"
        try:
            if not self.exists('/home/{}/.ensure_dir/logs_ensured'.format(
                    self.cli_args.get('os_user'))):
                if not self.exists(self.cli_args.get('dlab_path')):
                    self.console.sudo(
                        "mkdir -p " + self.cli_args.get('dlab_path'))
                    self.console.sudo('chown -R {} {} '.format(
                        self.cli_args.get('os_user'),
                        self.cli_args.get('dlab_path')))
            if not self.exists(log_root_dir):
                self.console.sudo(
                    'mkdir -p {}/provisioning'.format(log_root_dir))
                self.console.sudo(
                    'touch {}/provisioning/provisioning.log'.format(
                        log_root_dir))
                if not self.exists(supervisor_log_file):
                    self.console.sudo("mkdir -p /var/log/application")
                    self.console.sudo("touch " + supervisor_log_file)
                self.console.sudo("chown -R {0} {1}".format(
                    self.cli_args.get('os_user'), log_root_dir))
                self.console.sudo(
                    'touch /home/{}/.ensure_dir/logs_ensured'.format(
                        self.cli_args.get('os_user')))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def ensure_jre_jdk_endpoint(self):
        commands = [
            'apt-get install -y openjdk-8-jre-headless',
            'apt-get install -y openjdk-8-jdk-headless',
            'touch /home/{}/.ensure_dir/jre_jdk_ensured'.format(
                self.cli_args.get('os_user')),
        ]
        try:
            if not self.exists('/home/{}/.ensure_dir/jre_jdk_ensured'.format(
                    self.cli_args.get('os_user'))):
                for command in commands:
                    self.console.sudo(command)
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def ensure_supervisor_endpoint(self):
        commands = [
            'apt-get -y install supervisor',
            'update-rc.d supervisor defaults',
            'update-rc.d supervisor enable',
            'touch /home/{}/.ensure_dir/superv_ensured'.format(
                self.cli_args.get('os_user')),
        ]
        try:
            if not self.exists('/home/{}/.ensure_dir/superv_ensured'.format(
                    self.cli_args.get('os_user'))):
                for command in commands:
                    self.console.sudo(command)

        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def ensure_docker_endpoint(self):
        try:
            if not self.exists('/home/{}/.ensure_dir/docker_ensured'.format(
                    self.cli_args.get('os_user'))):
                self.console.sudo(
                    "bash -c 'curl -fsSL "
                    "https://download.docker.com/linux/ubuntu/gpg"
                    " | apt-key add -'")
                self.console.sudo(
                    'add-apt-repository "deb [arch=amd64] '
                    'https://download.docker.com/linux/ubuntu '
                    '$(lsb_release -cs) stable"')
                self.console.sudo('apt-get update')
                self.console.sudo('apt-cache policy docker-ce')
                self.console.sudo('apt-get install -y docker-ce={}'
                                  .format(self.cli_args.get('docker_version')))
                if not self.exists(
                        '{}/tmp'.format(self.cli_args.get('dlab_path'))):
                    self.console.run('mkdir -p {}/tmp'.format(
                        self.cli_args.get('dlab_path')))
                self.console.put('./daemon.json',
                                 '{}/tmp/daemon.json'.format(
                                     self.cli_args.get('dlab_path')))
                self.console.sudo(
                    'sed -i "s|REPOSITORY|{}:{}|g" {}/tmp/daemon.json'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('dlab_path')))
                if self.cli_args.get('cloud_provider') == "aws":
                    dns_ip_resolve = self.console.run(
                        "systemd-resolve --status "
                        "| grep -A 5 'Current Scopes: DNS' "
                        "| grep 'DNS Servers:' "
                        "| awk '{print $3}'")
                    self.console.sudo('sed -i "s|DNS_IP_RESOLVE|\"dns\": '
                                      '[{0}],|g" {1}/tmp/daemon.json'
                                      .format(dns_ip_resolve,
                                              self.cli_args.get('dlab_path')))
                elif self.cli_args.get('cloud_provider') == "gcp":
                    dns_ip_resolve = ""
                    self.console.sudo('sed -i "s|DNS_IP_RESOLVE||g" '
                                      '{1}/tmp/daemon.json'
                                      .format(dns_ip_resolve,
                                              self.cli_args.get('dlab_path')))
                self.console.sudo('mv {}/tmp/daemon.json /etc/docker'
                                  .format(self.cli_args.get('dlab_path')))
                self.console.sudo('usermod -a -G docker {}'
                                  .format(self.cli_args.get('os_user')))
                self.console.sudo('update-rc.d docker defaults')
                self.console.sudo('update-rc.d docker enable')
                self.console.sudo('service docker restart')
                self.console.sudo('touch /home/{}/.ensure_dir/docker_ensured'
                                  .format(self.cli_args.get('os_user')))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def create_key_dir_endpoint(self):
        try:
            if not self.exists(
                    '/home/{}/keys'.format(self.cli_args.get('os_user'))):
                self.console.run('mkdir /home/{}/keys'
                                 .format(self.cli_args.get('os_user')))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def configure_keystore_endpoint(self, os_user):
        try:
            if self.cli_args.get('cloud_provider') == "aws":
                self.console.sudo('apt-get install -y awscli')
            if not self.exists('/home/{}/keys/endpoint.keystore.jks'.format(
                    self.cli_args.get('os_user'))):
                self.console.sudo(
                    'aws s3 cp s3://{0}/dlab/certs/endpoint/'
                    'endpoint.keystore.jks '
                    '/home/{1}/keys/endpoint.keystore.jks'.format(
                        self.cli_args.get('ssn_bucket_name'),
                        self.cli_args.get('os_user')))
                if not self.exists('/home/{}/keys/dlab.crt'.format(
                        self.cli_args.get('os_user'))):
                    self.console.sudo(
                        'aws s3 cp s3://{0}/dlab/certs/endpoint/endpoint.crt'
                        ' /home/{1}/keys/endpoint.crt'.format(
                            self.cli_args.get('ssn_bucket_name'),
                            self.cli_args.get('os_user')))
                if not self.exists('/home/{}/keys/ssn.crt'.format(
                        self.cli_args.get('os_user'))):
                    self.console.sudo(
                        'aws s3 cp s3://{0}/dlab/certs/ssn/ssn.crt '
                        '/home/{1}/keys/ssn.crt'.format(
                            self.cli_args.get('ssn_bucket_name'),
                            self.cli_args.get('os_user')))
            elif self.cli_args.get('cloud_provider') == "gcp":
                if not self.exists(
                        '/home/{}/keys/endpoint.keystore.jks'.format(
                            self.cli_args.get('os_user'))):
                    self.console.sudo(
                        'gsutil -m cp -r '
                        'gs://{0}/dlab/certs/endpoint/endpoint.keystore.jks '
                        '/home/{1}/keys/'.format(
                            self.cli_args.get('ssn_bucket_name'),
                            self.cli_args.get('os_user')))
                if not self.exists('/home/{}/keys/dlab.crt'.format(
                        self.cli_args.get('os_user'))):
                    self.console.sudo(
                        'gsutil -m cp -r gs://{0}/dlab/certs/'
                        'endpoint/endpoint.crt'
                        ' /home/{1}/keys/'.format(
                            self.cli_args.get('ssn_bucket_name'),
                            self.cli_args.get('os_user')))
                if not self.exists('/home/{}/keys/ssn.crt'.format(
                        self.cli_args.get('os_user'))):
                    self.console.sudo('gsutil -m cp -r '
                                      'gs://{0}/dlab/certs/ssn/ssn.crt '
                                      '/home/{1}/keys/')
                if not self.exists('/home/{}/.ensure_dir/cert_imported'.format(
                        self.cli_args.get('os_user'))):
                    self.console.sudo(
                        'keytool -importcert -trustcacerts -alias dlab -file '
                        '/home/{0}/keys/endpoint.crt -noprompt -storepass '
                        'changeit -keystore {1}/lib/security/cacerts'.format(
                            os_user, self.java_home))
                self.console.sudo(
                    'keytool -importcert -trustcacerts -file '
                    '/home/{0}/keys/ssn.crt -noprompt -storepass '
                    'changeit -keystore {1}/lib/security/cacerts'.format(
                        os_user, self.java_home))
                self.console.sudo(
                    'touch /home/{}/.ensure_dir/cert_imported'.format(
                        self.cli_args.get('os_user')))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def configure_supervisor_endpoint(self):
        try:
            if not self.exists(
                    '/home/{}/.ensure_dir/configure_supervisor_ensured'.format(
                        self.cli_args.get('os_user'))):
                supervisor_conf = '/etc/supervisor/conf.d/supervisor_svc.conf'
                if not self.exists(
                        '{}/tmp'.format(self.cli_args.get('dlab_path'))):
                    self.console.run('mkdir -p {}/tmp'.format(
                        self.cli_args.get('dlab_path')))
                self.console.put('./supervisor_svc.conf',
                                 '{}/tmp/supervisor_svc.conf'
                                 .format(self.cli_args.get('dlab_path')))
                dlab_conf_dir = '{}/conf/'.format(
                    self.cli_args.get('dlab_path'))
                if not self.exists(dlab_conf_dir):
                    self.console.run('mkdir -p {}'.format(dlab_conf_dir))
                web_path = '{}/webapp'.format(self.cli_args.get('dlab_path'))
                if not self.exists(web_path):
                    self.console.run('mkdir -p {}'.format(web_path))
                if self.cli_args.get('cloud_provider') == 'aws':
                    interface = self.console.sudo(
                        'curl http://169.254.169.254/latest/meta-data/'
                        'network/interfaces/macs/')
                    self.cli_args['vpc_id'] = self.console.sudo(
                        'curl http://169.254.169.254/latest/meta-data/'
                        'network/interfaces/macs/{}/'
                        'vpc-id'.format(interface))
                    self.cli_args['subnet_id'] = self.console.sudo(
                        'curl http://169.254.169.254/latest/meta-data/'
                        'network/interfaces/macs/{}/'
                        'subnet-id'.format(interface))
                    self.cli_args['vpc2_id'] = self.cli_args.get('vpc_id')
                    self.cli_args['subnet2_id'] = self.cli_args.get(
                        'subnet_id')
                self.console.sudo(
                    'sed -i "s|OS_USR|{}|g" {}/tmp/supervisor_svc.conf'.format(
                        self.cli_args.get('os_user'),
                        self.cli_args.get('dlab_path')))
                self.console.sudo(
                    'sed -i "s|WEB_CONF|{}|g" '
                    '{}/tmp/supervisor_svc.conf'.format(
                        dlab_conf_dir, self.cli_args.get('dlab_path')))
                self.console.sudo(
                    'sed -i \'s=WEB_APP_DIR={}=\' '
                    '{}/tmp/supervisor_svc.conf'.format(
                        web_path, self.cli_args.get('dlab_path')))
                self.console.sudo('cp {}/tmp/supervisor_svc.conf {}'.format(
                    self.cli_args.get('dlab_path'), supervisor_conf))
                self.console.put('./provisioning.yml',
                                 '{}provisioning.yml'.format(dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|KEYNAME|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('key_name'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|KEYSTORE_PASSWORD|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('endpoint_keystore_password'),
                        dlab_conf_dir))
                self.console.sudo('sed -i "s|JRE_HOME|{}|g" {}provisioning.yml'
                                  .format(self.java_home, dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|CLOUD_PROVIDER|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('cloud_provider'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|MONGO_HOST|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('mongo_host'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|MONGO_PORT|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('mongo_port'), dlab_conf_dir))
                self.console.sudo('sed -i "s|SS_HOST|{}|g" {}provisioning.yml'
                                  .format(self.cli_args.get('ss_host'),
                                          dlab_conf_dir))
                self.console.sudo('sed -i "s|SS_PORT|{}|g" {}provisioning.yml'
                                  .format(self.cli_args.get('ss_port'),
                                          dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|KEYCLOACK_HOST|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('keycloack_host'), dlab_conf_dir))

                self.console.sudo(
                    'sed -i "s|CLIENT_SECRET|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('keycloak_client_secret'),
                        dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|CONF_OS|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('env_os'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|SERVICE_BASE_NAME|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('service_base_name'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|EDGE_INSTANCE_SIZE|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('edge_instence_size'),
                        dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|SUBNET_ID|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('subnet_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|REGION|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('region'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|ZONE|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('zone'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|TAG_RESOURCE_ID|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('tag_resource_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|SG_IDS|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('ssn_k8s_sg_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|SSN_INSTANCE_SIZE|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('ssn_instance_size'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|VPC2_ID|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('vpc2_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|SUBNET2_ID|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('subnet2_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|CONF_KEY_DIR|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('conf_key_dir'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|VPC_ID|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('vpc_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|PEERING_ID|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('peering_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|AZURE_RESOURCE_GROUP_NAME|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('azure_resource_group_name'),
                        dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|AZURE_SSN_STORAGE_ACCOUNT_TAG|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('azure_ssn_storage_account_tag'),
                        dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|AZURE_SHARED_STORAGE_ACCOUNT_TAG|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('azure_shared_storage_account_tag'),
                        dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|AZURE_DATALAKE_TAG|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('azure_datalake_tag'),
                        dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|AZURE_CLIENT_ID|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('azure_client_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|GCP_PROJECT_ID|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('gcp_project_id'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|LDAP_HOST|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('ldap_host'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|LDAP_DN|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('ldap_dn'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|LDAP_OU|{}|g" {}provisioning.yml'.format(
                        self.cli_args.get('ldap_users_group'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|LDAP_USER_NAME|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('ldap_user'), dlab_conf_dir))
                self.console.sudo(
                    'sed -i "s|LDAP_USER_PASSWORD|{}|g" '
                    '{}provisioning.yml'.format(
                        self.cli_args.get('ldap_bind_creds'), dlab_conf_dir))
                self.console.sudo(
                    'touch /home/{}/.ensure_dir/'
                    'configure_supervisor_ensured'.format(
                        self.cli_args.get('os_user')))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def ensure_jar_endpoint(self):
        try:
            ensure_file = ('/home/{}/.ensure_dir/backend_jar_ensured'
                           .format(self.cli_args.get('os_user')))
            if not self.exists(ensure_file):
                web_path = '{}/webapp'.format(self.cli_args.get('dlab_path'))
                if not self.exists(web_path):
                    self.console.run('mkdir -p {}'.format(web_path))
                if self.cli_args.get('cloud_provider') == "aws":
                    self.console.run(
                        'wget -P {}  --user={} --password={} '
                        'https://{}/repository/packages/aws/'
                        'provisioning-service-2.1.jar '
                        '--no-check-certificate'.format(
                            web_path, self.cli_args.get('repository_user'),
                            self.cli_args.get('repository_pass'),
                            self.cli_args.get('repository_address')))
                elif self.cli_args.get('cloud_provider') == "gcp":
                    self.console.run(
                        'wget -P {}  --user={} --password={} '
                        'https://{}/repository/packages/gcp/'
                        'provisioning-service-2.1.jar '
                        '--no-check-certificate'.format(
                            web_path, self.cli_args.get('repository_user'),
                            self.cli_args.get('repository_pass'),
                            self.cli_args.get('repository_address')))
                    self.console.run(
                        'mv {0}/*.jar {0}/provisioning-service.jar'.format(
                            web_path))
                    self.console.sudo('touch {}'.format(ensure_file))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def start_supervisor_endpoint(self):
        try:
            self.console.sudo("service supervisor restart")
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def get_sources(self):
        try:
            self.console.run(
                "git clone https://github.com/apache/incubator-dlab.git "
                "{0}/sources".format(self.cli_args.get('dlab_path')))
            if self.cli_args.get('branch_name') != "":
                self.console.run("cd {0}/sources && git checkout {1} && cd"
                                 .format(self.cli_args.get('dlab_path'),
                                         self.cli_args.get('branch_name')))
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def pull_docker_images(self):
        try:
            ensure_file = ('/home/{}/.ensure_dir/docker_images_pulled'
                           .format(self.cli_args.get('os_user')))
            if self.exists(ensure_file):
                self.console.sudo(
                    'docker login -u {} -p {} {}:{}'.format(
                        self.cli_args.get('repository_user'),
                        self.cli_args.get('repository_pass'),
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-base-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-edge-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-project-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-jupyter-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-rstudio-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-zeppelin-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-tensor-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-tensor-rstudio-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-deeplearning-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.'
                    'dlab-dataengine-service-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker pull {}:{}/docker.dlab-dataengine-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-base-{} '
                    'docker.dlab-base'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-edge-{} '
                    'docker.dlab-edge'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-project-{} '
                    'docker.dlab-project'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-jupyter-{} '
                    'docker.dlab-jupyter'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-rstudio-{} '
                    'docker.dlab-rstudio'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-zeppelin-{} '
                    'docker.dlab-zeppelin'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-tensor-{} '
                    'docker.dlab-tensor'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-tensor-rstudio-{} '
                    'docker.dlab-tensor-rstudio'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-deeplearning-{} '
                    'docker.dlab-deeplearning'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-dataengine-service-{} '
                    'docker.dlab-dataengine-service'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker tag {}:{}/docker.dlab-dataengine-{} '
                    'docker.dlab-dataengine'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-base-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-edge-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-project-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-jupyter-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-rstudio-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-zeppelin-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-tensor-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-tensor-rstudio-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-deeplearning-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-dataengine-service-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'docker rmi {}:{}/docker.dlab-dataengine-{}'.format(
                        self.cli_args.get('repository_address'),
                        self.cli_args.get('repository_port'),
                        self.cli_args.get('cloud_provider')))
                self.console.sudo(
                    'chown -R {0}:docker /home/{0}/.docker/'.format(
                        self.cli_args.get('os_user')))
                self.console.sudo('touch {}'.format(ensure_file))

        except Exception:
            traceback.print_exc()
            sys.exit(1)

    def update_system(self):
        self.command_executor.run('apt-get update')

    def init_dlab_connection(self):
        user_name = self.cli_args.get('os_user')
        key = self.cli_args.get('pkey')
        self.console = ParamikoCommandExecutor(self.master_ip,
                                               user_name, key)

    def set_java_home(self):
        command = (
            'bash -c "update-alternatives --query java | grep \'Value: \' '
            '| grep -o \'/.*/jre\'" ')
        self.java_home = (
            self.command_executor.sudo(command).stdout.rstrip("\n\r"))


class EndpointDestroyUseCase(DestroyUseCase):
    pass
