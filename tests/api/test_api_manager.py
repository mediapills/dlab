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
import sqlite3
import unittest

from api.managers import APIManager
from dlab_core.infrastructure.repositories import (SQLiteRepository,
                                                   FIFOSQLiteQueueRepository)


class BaseManager(unittest.TestCase):
    sql_create_table = """ CREATE TABLE `dlab` (
                                    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
                                    `request`	TEXT,
                                    `status`	INTEGER,
                                    `error`	TEXT,
                                    `resource`	TEXT,
                                    `action`	TEXT,
                                    `created`	TEXT,
                                    `updated`	TEXT
                                    ); """
    db_name = 'data.db'

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        cls.db_file_path = os.path.join(cls.base_dir, cls.db_name)
        with sqlite3.connect(os.path.join(cls.base_dir, cls.db_name)) as con:
            cursor = con.cursor()
            cursor.execute(cls.sql_create_table)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.db_file_path)


class TestAPIManager(BaseManager):

    def setUp(self):
        self.api_manager = APIManager(self.base_dir)

    def tearDown(self):
        del self.api_manager

    def test_set_up_manager(self):
        self.assertEqual(self.api_manager.location,
                         self.base_dir)

        self.assertIsInstance(self.api_manager.repo, SQLiteRepository)
        self.assertIsInstance(self.api_manager.queue, FIFOSQLiteQueueRepository)

    def test_create_record(self):
        record_id = self.api_manager.create_record('data', 'resource', 'action')
        self.assertGreater(record_id, 0)
