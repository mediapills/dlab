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

        self.command_executor = command_executor
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
        self.configure_keystore_endpoint()
        self.ensure_jar_endpoint()
        self.get_sources()
        self.pull_docker_images()
        self.start_supervisor_endpoint()

    def exists(self, path):
        return self.cli_args.run('test -e {} && exists'.format(path))

    def run_bash(self, bash_script):
        try:
            print(self.command_executor.run(bash_script))
        except Exception:
            sys.exit(1)

    def create_user(self):
        command = '''
        export os_user={os_user} && \
        sudo_group={sudo_group} && \
        initial_user={initial_user} && \
        [ ! -f "/home/$initial_user/.ssh_user_ensured" ] && \
        sudo useradd -m -G $sudo_group -s /bin/bash $os_user && \
        sudo echo "$os_user ALL = (ALL) NOPASSWD:ALL" >> sudo /etc/sudoers && \
        sudo mkdir /home/$os_user/.ssh && \
        sudo chown -R $initial_user:$initial_user /home/$os_user/.ssh/ && \
        sudo cat /home/$initial_user/.ssh/authorized_keys > /home/$os_user/.ssh/authorized_keys && \
        sudo chown -R $os_user:$os_user /home/$os_user/.ssh/ && \
        sudo chmod 700 /home/$os_user/.ssh && \
        sudo chmod 600 /home/$os_user/.ssh/authorized_keys && \
        touch /home/$initial_user/.ssh_user_ensured 
        '''.format(os_user=self.cli_args.get('os_user'),
                      sudo_group='sudo',
                      initial_user='ubuntu')

        self.run_bash(command)

    def copy_keys(self):
        command = '''
        export pkey={pkey} \
        export os_user={os_user} \
        cp $pkey /home/$os_user/keys
        '''.format(pkey=self.cli_args.get('pkey'),
                   os_user=self.cli_args.get('os_user'))

        self.run_bash(command)

    def ensure_dir_endpoint(self):
        command = '''
        export os_user = {os_user} \
        mkdir -p /home/$os_user/.ensure_dir
        '''.format(os_user=self.cli_args.get('os_user'))

        self.run_bash(command)

    def ensure_logs_endpoint(self):
        command = '''
        export os_user={os_user} && \
        export dlab_path={dlab_path} && \
        export log_root_dir={log_root_dir} && \
        export supervisor_log_file={supervisor_log_file} && \
        [ ! -f "/home/$os_user/.ensure_dir/logs_ensured" ] && \
            mkdir -p $dlab_path && \
            chown -R $os_user $dlab_path && \
            mkdir -p $log_root_dir/provisioning && \
            touch $log_root_dir/provisioning/provisioning.log && \
            mkdir -p /var/log/application && \
            touch $supervisor_log_file && \
            chown -R $os_user $log_root_dir && \
            touch /home/$os_user/.ensure_dir/logs_ensured \
        fi
        '''.format(
            os_user=self.cli_args.get('os_user'),
            dlab_path=self.cli_args.get('dlab_path'),
            log_root_dir='/var/opt/dlab/log',
            supervisor_log_file='/var/log/application/provision-service.log')

        self.run_bash(command)

    def ensure_jre_jdk_endpoint(self):
        command = '''
        export os_user={os_user} && \
        [ ! -f "/home/$os_user/.ensure_dir/jre_jdk_ensured" ] && \
            apt-get install -y openjdk-8-jre-headless && \
            apt-get install -y openjdk-8-jdk-headless && \
            touch /home/$os_user/.ensure_dir/jre_jdk_ensured \
        fi'''.format(os_user=self.cli_args.get('os_user'))

        self.run_bash(command)

    def ensure_supervisor_endpoint(self):

        command = '''
        export os_user={os_user} && \
        [ ! -f /home/$os_user/.ensure_dir/superv_ensured ] && \
            apt-get -y install supervisor && \
            update-rc.d supervisor defaults && \
            update-rc.d supervisor enable && \
            touch /home/$os_user/.ensure_dir/superv_ensured \
        fi'''.format(os_user=self.cli_args.get('os_user'))

        self.run_bash(command)

    def ensure_docker_endpoint(self):

        command = '''
        export os_user={os_user} && \
        export docker_version={docker_version} && \
        export dlab_path={dlab_path} && \
        export repository_address={repository_address} && \
        export repository_port={repository_port} && \
        export cloud_provider={cloud_provider} && \
        [ ! -f /home/$os_user/.ensure_dir/docker_ensured ] && \
            bash -c 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg| apt-key add -' && \
            add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
            apt-get update && \
            apt-cache policy docker-ce && \
            apt-get install -y docker-ce=$docker_version && \
            mkdir -p $dlab_path/tmp && \
            cp ./daemon.json $dlab_path/tmp/daemon.json && \
            sed -i "s|REPOSITORY|$repository_address:$repository_port|g" $dlab_path/tmp/daemon.json && \
            [[$cloud_provider = aws]] && \
                dns_ip_resolve=systemd-resolve --status | grep -A 5 'Current Scopes: DNS' | grep 'DNS Servers:'| awk '{{print $3}}'  && \
                sed -i 's|DNS_IP_RESOLVE|\"dns\": [\"$dns_ip_resolve\"],|g' $dlab_path/tmp/daemon.json && \
            [[$cloud_provider = gcp]] then  && \
                    sed -i "s|DNS_IP_RESOLVE||g" $dlab_path/tmp/daemon.json && \
            mv $dlab_path/tmp/daemon.json /etc/docker && \
            usermod -a -G docker $os_user && \
            update-rc.d docker defaults && \
            update-rc.d docker enable && \
            service docker restart && \
            touch /home/$os_user/.ensure_dir/docker_ensured \
        fi'''.format(**self.cli_args)

        self.run_bash(command)

    def create_key_dir_endpoint(self):
        command = '''
        export os_user={os_user} && \
        mkdir -p /home/$os_user/keys
        '''.format(os_user=self.cli_args.get('os_user'))

        self.run_bash(command)

    def configure_keystore_endpoint(self):
        command = '''
        export os_user={os_user} && \
        export cloud_provider={cloud_provider} && \
        export ssn_bucket_name={ssn_bucket_name} && \
        export java_home={java_home} && \
        [[$cloud_provider = aws]] && \
            apt-get install -y awscli && \
            aws s3 cp s3://$ssn_bucket_name/dlab/certs/endpoint/endpoint.keystore.jks /home/$os_user/keys/endpoint.keystore.jks \
            [ ! -f /home/$os_user/keys/dlab.crt ] && \
            aws s3 cp s3://$ssn_bucket_name/dlab/certs/endpoint/endpoint.crt /home/$os_user/keys/endpoint.crt \
            [ ! -f /home/$os_user/keys/ssn.crt ] && \
            aws s3 cp s3://$ssn_bucket_name/dlab/certs/ssn/ssn.crt /home/$os_user/keys/ssn.crt \
        [[$cloud_provider = gcp]] && \
            [ ! -f /home/$os_user/keys/endpoint.keystore.jks ] && \
            gsutil -m cp -r gs://$ssn_bucket_name/dlab/certs/endpoint/endpoint.keystore.jks /home/$os_user/keys/ \
            [ ! -f /home/$os_user/keys/dlab.crt ] && \
            gsutil -m cp -r gs://$ssn_bucket_name/dlab/certs/endpoint/endpoint.crt /home/$os_user/keys/ \
            [ ! -f /home/$os_user/keys/ssn.crt ] && \
            gsutil -m cp -r gs://$ssn_bucket_name/dlab/certs/ssn/ssn.crt /home/$os_user/keys/ \
        [ ! -f /home/$os_user/.ensure_dir/cert_imported ] && \
            keytool -importcert -trustcacerts -alias dlab -file /home/$os_user/keys/endpoint.crt -noprompt -storepass changeit -keystore $java_home/lib/security/cacerts && \
            keytool -importcert -trustcacerts -file  /home/$os_user/keys/ssn.crt -noprompt  -storepass changeit -keystore $java_home/lib/security/cacerts && \
            touch /home/$os_user/.ensure_dir/cert_imported 
        '''.format(java_home=self.java_home, **self.cli_args)

        self.run_bash(command)

    def configure_supervisor_endpoint(self):
        command = '''
        export os_user={os_user} && \
        export dlab_path={dlab_path} && \
        export endpoint_keystore_password={endpoint_keystore_password} && \
        export key_name={key_name} && \
        export mongo_host={mongo_host} && \
        export mongo_port={mongo_port} && \
        export cloud_provider={cloud_provider} && \
        export supervisor_conf={supervisor_conf} && \
        export dlab_conf_dir=$dlab_path/conf && \
        export web_path=$dlab_path/webapp/ && \
        export vpc_id={vpc_id} && \
        export subnet_id={subnet_id} && \
        export vpc2_id={vpc_id} && \
        export subnet2_id={subnet_id} && \
        export ss_host={ss_host} && \
        export ss_port={ss_port} && \
        export keycloak_client_id={keycloak_client_id} && \
        export keycloack_host={keycloack_host} && \
        export keycloak_client_secret={keycloak_client_secret} && \
        export mongo_password={mongo_password} && \
        export env_os={env_os} && \
        export service_base_name={service_base_name} && \
        export edge_instence_size={edge_instence_size} && \
        export subnet_id={subnet_id} && \
        export region={region} && \
        export zone={zone} && \
        export tag_resource_id={tag_resource_id} && \
        export ssn_k8s_sg_id={ssn_k8s_sg_id} && \
        export ssn_instance_size={ssn_instance_size} && \
        export vpc2_id={vpc2_id} && \
        export subnet2_id={subnet2_id} && \
        export conf_key_dir={conf_key_dir} && \
        export vpc_id={vpc_id} && \
        export peering_id={peering_id} && \
        export azure_resource_group_name={azure_resource_group_name} && \
        export azure_ssn_storage_account_tag={azure_ssn_storage_account_tag} && \
        export azure_shared_storage_account_tag={azure_shared_storage_account_tag} && \
        export azure_datalake_tag={azure_datalake_tag} && \
        export azure_client_id={azure_client_id} && \
        export gcp_project_id={gcp_project_id} && \
        export ldap_host={ldap_host} && \
        export ldap_dn={ldap_dn} && \
        export ldap_users_group={ldap_users_group} && \
        export ldap_user={ldap_user} && \
        export ldap_bind_creds={ldap_bind_creds} && \
        if ! -f /home/$os_user/.ensure_dir/configure_supervisor_ensured then && \
            mkdir -p $dlab_path/tmp && 
            cp ./supervisor_svc.conf $dlab_path/tmp/supervisor_svc.conf && \
            mkdir -p $dlab_conf_dir && \
            mkdir -p web_path && \
            if [[$cloud_provider = aws]] then \
                interface=curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/ && \
                vpc_id=curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/$interface/vpc-id && \
                subnet_id=curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/$interface/subnet-id && \
                vpc2_id=vpc_id && \
                subnet2_id=subnet_id && \
            fi\
            sed -i "s|OS_USR|$os_user|g" $dlab_path/tmp/supervisor_svc.conf && \
            sed -i "s|WEB_CONF|$dlab_conf_dir|g" $dlab_path/tmp/supervisor_svc.conf && \
            sed -i \'s=WEB_APP_DIR=$web_path=\' $dlab_path/tmp/supervisor_svc.conf && \
            cp $dlab_path/tmp/supervisor_svc.conf $supervisor_conf && \
            cp ./provisioning.yml $dlab_conf_dir/provisioning.yml && \
            sed -i "s|KEYNAME|$key_name|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|KEYSTORE_PASSWORD|$endpoint_keystore_password|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|JRE_HOME|$java_home|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|CLOUD_PROVIDER|$cloud_provider|g" dlab_conf_dir/provisioning.yml && \
            sed -i "s|MONGO_HOST|$mongo_host|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|MONGO_PORT|$mongo_port|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|SS_HOST|$ss_host|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|SS_PORT|$ss_port|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|KEYCLOACK_HOST|$keycloack_host|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|CLIENT_ID|$keycloak_client_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|CLIENT_SECRET|$keycloak_client_secret|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|MONGO_PASSWORD|$mongo_password|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|CONF_OS|$env_os|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|SERVICE_BASE_NAME|$service_base_name|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|EDGE_INSTANCE_SIZE|$edge_instence_size|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|SUBNET_ID|$subnet_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|REGION|$region|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|ZONE|$zone|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|TAG_RESOURCE_ID|$tag_resource_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|SG_IDS|$ssn_k8s_sg_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|SSN_INSTANCE_SIZE|$ssn_instance_size|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|VPC2_ID|$vpc2_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|SUBNET2_ID|$subnet2_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|CONF_KEY_DIR|$conf_key_dir|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|VPC_ID|$vpc_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|PEERING_ID|$peering_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|AZURE_RESOURCE_GROUP_NAME|$azure_resource_group_name|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|AZURE_SSN_STORAGE_ACCOUNT_TAG|$azure_ssn_storage_account_tag|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|AZURE_SHARED_STORAGE_ACCOUNT_TAG|$azure_shared_storage_account_tag|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|AZURE_DATALAKE_TAG|$azure_datalake_tag|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|AZURE_CLIENT_ID|$azure_client_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|GCP_PROJECT_ID|$gcp_project_id|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|LDAP_HOST|$ldap_host|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|LDAP_DN|$ldap_dn|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|LDAP_OU|$ldap_users_group|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|LDAP_USER_NAME|$ldap_user|g" $dlab_conf_dir/provisioning.yml && \
            sed -i "s|LDAP_USER_PASSWORD|$ldap_bind_creds|g" $dlab_conf_dir/provisioning.yml && \
            touch /home/$os_user/.ensure_dir/configure_supervisor_ensured  \
        fi'''.format(
            supervisor_conf='/etc/supervisor/conf.d/supervisor_svc.conf',
            **self.cli_args)

        self.run_bash(command)

    def ensure_jar_endpoint(self):
        command = '''
        export web_path={dlab_path}/webapp \
        export cloud_provider={cloud_provider} \
        export repository_user={repository_user} \
        export repository_address={repository_address} \
        if ! -f /home/$os_user/.ensure_dir/backend_jar_ensured then \
            mkdir -p $web_path && \
             if [[$cloud_provider = aws]] then \
                wget -P $web_path --user=$repository_user --password={repository_pass} https://$repository_address/repository/packages/aws/provisioning-service-2.1.jar --no-check-certificate && \
             else \
                if [[$cloud_provider = gcp]] then \
                    wget -P $web_path --user=$repository_user --password={repository_pass} https://$repository_address/repository/gcp/aws/provisioning-service-2.1.jar --no-check-certificate && \
                fi\
             fi\
             mv $web_path/*.jar $web_path/provisioning-service.jar && \
             touch /home/$os_user/.ensure_dir/backend_jar_ensured \
        fi'''.format(**self.cli_args)

        self.run_bash(command)

    def start_supervisor_endpoint(self):
        command = 'service supervisor restart'
        self.run_bash(command)

    def get_sources(self):
        command = '''
        export dlab_path={dlab_path} \
        export branch_name={branch_name} \
        git clone https://github.com/apache/incubator-dlab.git $dlab_path/sources && \
        if [[! -z "$branch_name"]] then \
            cd $dlab_path/sources && git checkout $branch_name && cd \
        fi'''.format(**self.cli_args)

        self.run_bash(command)

    def pull_docker_images(self):
        command = '''
        export repository_user={repository_user} \
        export repository_pass={repository_pass} \
        export repository_address={repository_address} \
        export repository_port={repository_port} \
        export cloud_provider={cloud_provider} \
        if ! -f /home/$os_user/.ensure_dir/docker_images_pulled then \
            docker login -u $repository_user -p $repository_pass $repository_address:$repository_port && \
            docker pull $repository_address:$repository_port/docker.dlab-edge-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-project-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-jupyter-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-rstudio-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-zeppelin-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-tensor-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-tensor-rstudio-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-deeplearning-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-dataengine-service-$cloud_provider && \
            docker pull $repository_address:$repository_port/docker.dlab-dataengine-$cloud_provider && \
            docker tag $repository_address:$repository_port/docker.dlab-base-$cloud_provider docker.dlab-base && \
            docker tag $repository_address:$repository_port/docker.dlab-edge-$cloud_provider docker.dlab-edge && \
            docker tag $repository_address:$repository_port/docker.dlab-project-$cloud_provider docker.dlab-project && \
            docker tag $repository_address:$repository_port/docker.dlab-jupyter-$cloud_provider docker.dlab-jupyter && \
            docker tag $repository_address:$repository_port/docker.dlab-rstudio-$cloud_provider docker.dlab-rstudio && \
            docker tag $repository_address:$repository_port/docker.dlab-zeppelin-$cloud_provider docker.dlab-zeppelin && \
            docker tag $repository_address:$repository_port/docker.dlab-tensor-$cloud_provider docker.dlab-tensor && \
            docker tag $repository_address:$repository_port/docker.dlab-tensor-rstudio-$cloud_provider docker.dlab-tensor-rstudio && \
            docker tag $repository_address:$repository_port/docker.dlab-deeplearning-$cloud_provider docker.dlab-deeplearning && \
            docker tag $repository_address:$repository_port/docker.dlab-dataengine-service-$cloud_provider docker.dlab-dataengine-service && \
            docker tag $repository_address:$repository_port/docker.dlab-dataengine-$cloud_provider docker.dlab-dataengine && \
            docker rmi $repository_address:$repository_port/docker.dlab-base-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-edge-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-project-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-jupyter-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-rstudio-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-zeppelin-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-tensor-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-tensor-rstudio-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-deeplearning-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-dataengine-service-$cloud_provider && \
            docker rmi $repository_address:$repository_port/docker.dlab-dataengine-$cloud_provider && \
            chown -R $os_user:docker /home/$os_user/.docker/ && \
            touch /home/$os_user/.ensure_dir/docker_images_pulled \
        fi'''.format(**self.cli_args)

        self.run_bash(command)

    def update_system(self):
        self.command_executor.run('apt-get update')

    def init_dlab_connection(self):
        user_name = self.cli_args.get('os_user')
        key = self.cli_args.get('pkey')
        self.command_executor = ParamikoCommandExecutor(self.master_ip, user_name, key)
        print('change console')

    def set_java_home(self):
        command = ('bash -c "update-alternatives --query java '
                   '| grep \'Value: \' | grep -o \'/.*/jre\'" ')
        self.java_home = (
            self.command_executor.sudo(command).rstrip("\n\r"))


class EndpointDestroyUseCase(DestroyUseCase):
    pass


class ProjectProvisionUseCase(ProvisionUseCase):
    pass


class ProjectDestroyUseCase(DestroyUseCase):
    pass
