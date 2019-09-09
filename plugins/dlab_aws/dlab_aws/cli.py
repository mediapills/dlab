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

from dlab_aws.infrastructure.controllers.deployment import AWSCLIController

COMPONENT_SSN = 'ssn'
COMPONENT_ENDPOINT = 'endpoint'

ACTION_DEPLOY = 'deploy'
ACTION_DESTROY = 'destroy'

DEPLOY_ROUTES = [{
    'func': AWSCLIController.deploy_ssn,
    'args': [None, COMPONENT_SSN, ACTION_DEPLOY]
}, {
    'func': AWSCLIController.destroy_ssn,
    'args': [None, COMPONENT_SSN, ACTION_DESTROY]
}, {
    'func': AWSCLIController.deploy_endpoint,
    'args': [None, COMPONENT_ENDPOINT, ACTION_DEPLOY]
}, {
    'func': AWSCLIController.destroy_endpoint,
    'args': [None, COMPONENT_ENDPOINT, ACTION_DESTROY]
}]
