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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseQueue:

    @abc.abstractmethod
    def add(self, item):
        """
        Add elements at the tail of queue. More specifically, at the last of
        linked list if it is used, or according to the priority in case of
        priority queue implementation.

        :param item:
        :return:
        """
        pass

    @abc.abstractmethod
    def get(self):
        """
        View the head of queue without removing it. It returns Null if the
        queue is empty.

        :return:
        """
        pass

    @abc.abstractmethod
    def done(self):
        """
        Indicate that a formerly enqueued task is complete.

        :return:
        """
        pass

    @abc.abstractmethod
    def size(self):
        """
        This method return the number of elements in the queue.

        :return:
        """
        pass
