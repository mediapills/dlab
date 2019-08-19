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
import signal
import sys

from dlab_core.domain.exceptions import DLabException
from dlab_core.registry import load_plugins, get_resource


class BaseCliHandler(object):
    HELP_OPTIONS = ('-h', '--help')

    def __init__(self, next_handler=None):
        self._next_handler = next_handler

    @property
    def next_handler(self):
        return self._next_handler

    @next_handler.setter
    def next_handler(self, handler):
        self._next_handler = handler

    def parse_args(self):
        raise NotImplementedError

    def execute(self):
        try:
            self.parse_args()
            if self.next_handler is not None:
                get_resource(self.next_handler)()
        except KeyboardInterrupt:
            # Shell standard for signals that terminate
            # the process is to return 128 + signum, in this case
            # SIGINT=2, so we'll have an RC of 130.
            return 128 + signal.SIGINT
        except DLabException:
            # debug: "Exception caught in dlab"
            return 255
        except Exception:
            # Exception caught in main()"
            return 255


class DeployCliHandler(BaseCliHandler):
    @property
    def next_handler(self):
        return 'deploy.cli.parser'

    def parse_args(self):
        usage = 'usage: dlab deploy\n'
        action = len(sys.argv) > 1 and sys.argv[1]

        if action in self.HELP_OPTIONS:
            sys.stdout.write(usage)
            exit(0)

        if not action or action != 'deploy':
            sys.stderr.write(usage)
            exit(1)


def main():
    load_plugins()
    driver = DeployCliHandler()
    driver.execute()
