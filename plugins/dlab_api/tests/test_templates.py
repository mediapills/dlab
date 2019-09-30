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
from tests.base_test import BaseTestAPI


class TestTemplateAPI(BaseTestAPI):

    def test_get_template_by_valid_type(self):
        resp = self.client.get('/template/exploratory')

        self.assertDictEqual(resp.json, {})

    def test_get_template_by_in_valid_type(self):
        resp = self.client.get('/template/test')

        self.assertEqual(resp.json['code'], 0)
