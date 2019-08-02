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

from dlab_core.domain.exceptions import DLabException
from dlab_core.registry import load_plugins


def main():
    driver = create_clidriver()
    rc = driver.main()
    return rc


def create_clidriver():
    """ CLIDriver Builder.

    :rtype: CLIDriver
    :return: CLIDriver instance.
    """

    return CLIDriver()


class CLIDriver(object):

    def __init__(self):
        """CLIDriver constructor."""
        pass

    def main(self):
        """Manage main CLI execution flow."""

        try:
            self.execute()
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

    @staticmethod
    def execute():
        # TODO Finish implementation
        # context = load_plugins()
        load_plugins()
