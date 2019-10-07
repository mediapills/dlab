import os
import subprocess
import sys
from threading import Thread

from api.command_builder import CommandBuilder
from api.models import DlabModel, FIFOModel
from dlab_core.infrastructure.repositories import (
    SQLiteRepository, STARTED, DONE, STATUSES,
    PROCESSED, ERROR, FIFOSQLiteQueueRepository)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
num_worker_threads = 2


class DaemonManagerException(Exception):
    pass


class BaseManager(object):
    def __init__(self, location=None):
        if location is None:
            location = os.path.join(BASE_DIR, 'database')
        self.location = location
        self.queue = FIFOSQLiteQueueRepository(location)
        self.repo = SQLiteRepository(os.path.join(location, 'data.db'))


class APIManager(BaseManager):
    def create_record(self, data, resource, action):
        record_id = self.repo.insert(
            DlabModel(request=data, resource=resource, action=action,
                      status=STATUSES[PROCESSED])
        )
        self.queue.insert(FIFOModel(id=record_id))
        return record_id


class DaemonManager(BaseManager):
    def __init__(self, location=None):
        super(DaemonManager, self).__init__(location)
        for i in range(num_worker_threads):
            t = Thread(target=self.run)
            t.start()

    def run(self):
        while True:
            record_id = self.start_task()
            try:
                cmd = self.get_execution_command(record_id)
                p = subprocess.Popen(cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=True)
                out, err = p.communicate()
                if err:
                    raise DaemonManagerException(err)

                self.finish_task(record_id)

            except DaemonManagerException as e:
                self.process_error(record_id, str(e))

    def finish_task(self, record_id):
        self.queue.delete()
        self.repo.update(DlabModel(id=record_id, status=STATUSES[DONE]))

    def process_error(self, record_id, message):
        self.repo.update(
            DlabModel(id=record_id, status=STATUSES[ERROR], error=message)
        )

    def start_task(self):
        record_id = self.queue.get()
        self.repo.update(DlabModel(id=record_id, status=STATUSES[STARTED]))
        return record_id

    def get_execution_command(self, record_id):
        entity = self.repo.find_one(record_id)
        builder = CommandBuilder(**entity)
        return builder.build_cmd()


if __name__ == '__main__':
    m = DaemonManager()
    try:
        m.run()
    except KeyboardInterrupt:
        sys.exit(0)
