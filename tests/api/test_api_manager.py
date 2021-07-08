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
import unittest

from api.managers import APIManager
from dlab_core.infrastructure.repositories import (SQLiteRepository,
                                                   FIFOSQLiteQueueRepository)


class TestAPIManager(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.api_manager = APIManager(
            os.path.join(self.base_dir, '..', 'database')
        )

    def tearDown(self):
        del self.api_manager

    def test_set_up_manager(self):
        self.assertIsInstance(self.api_manager.repo, SQLiteRepository)
        self.assertIsInstance(self.api_manager.queue, FIFOSQLiteQueueRepository)

    def test_create_record(self):
        record_id = self.api_manager.create_record('data', 'resource', 'action')
        self.assertGreater(record_id, 0)
