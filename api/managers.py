import logging
import os
import subprocess
import sys
from threading import Thread

from api.command_builder import CommandBuilder
from api.models import DlabModel, FIFOModel
from dlab_core.infrastructure.repositories import (
    SQLiteRepository, STARTED, DONE, STATUSES,
    PROCESSED, ERROR, FIFOSQLiteQueueRepository, STATUSES_BY_NUM)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
num_worker_threads = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",  # noqa E501
    handlers=[
        logging.StreamHandler()
    ])


class DaemonManagerException(Exception):
    pass


class BaseManager(object):
    def __init__(self, location=None):
        if location is None:
            location = os.path.join(BASE_DIR, 'database')
        self.location = location
        self.logging = logging.getLogger(__name__)
        self.queue = FIFOSQLiteQueueRepository(location)
        self.repo = SQLiteRepository(location)


class APIManager(BaseManager):
    def create_record(self, data, resource, action):
        self.logging.info('Create record')
        record_id = self.repo.insert(
            DlabModel(request=data, resource=resource, action=action,
                      status=STATUSES[PROCESSED])
        )
        self.queue.insert(FIFOModel(id=record_id))
        return record_id

    def get_record(self, id):
        return self.repo.find_one(id)


class DaemonManager(BaseManager):
    def __init__(self, location=None):
        super(DaemonManager, self).__init__(location)
        self.logging.info('Init treads')

        for i in range(num_worker_threads):
            t = Thread(target=self.run)
            t.start()

    def run(self):
        self.logging.info('Run thread')
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
        self.logging.info('Finish task {}'.format(record_id))
        self.queue.delete()
        self.repo.update(DlabModel(id=record_id, status=STATUSES[DONE]))

    def process_error(self, record_id, message):
        self.logging.error('Process error {}'.format(record_id))

        self.repo.update(
            DlabModel(id=record_id, status=STATUSES[ERROR], error=message)
        )

    def start_task(self):
        record_id = self.queue.get()
        self.logging.info('Start task {}'.format(record_id))
        self.repo.update(DlabModel(id=record_id, status=STATUSES[STARTED]))
        return record_id

    def get_execution_command(self, record_id):
        self.logging.info('Get execution command')
        entity = self.repo.find_one(record_id)
        builder = CommandBuilder(**entity)
        return builder.build_cmd()


if __name__ == '__main__':
    m = DaemonManager()
    try:
        m.run()
    except KeyboardInterrupt:
        sys.exit(0)
