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
from dlab_core.domain.exceptions import DLabException

LC_ERR_INVALID_PARAMETER_TYPE = (
    'Invalid parameter {} of type {}, should be {}')


def validate_property_type(exp_type):
    def validate(fn):
        def wrapper(*args, **kwargs):
            argument = args[1]
            if not isinstance(argument, exp_type):
                raise DLabException(LC_ERR_INVALID_PARAMETER_TYPE.format(
                    argument, type(argument).__name__, exp_type.__name__))
            return fn(*args, **kwargs)

        return wrapper

    return validate
