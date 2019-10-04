import subprocess
import sys
from threading import Thread

import persistqueue

from dlab_core.infrastructure.repositories import SQLiteRepository, STARTED, DONE

DB_PATH = 'C:\Users\Dmytro_Khanas\projects\dlab'
num_worker_threads = 2


class BaseManager(object):
    def __init__(self, location=None):
        if location is None:
            location = DB_PATH
        self.location = location
        self.queue = persistqueue.FIFOSQLiteQueue(location, multithreading=True, auto_commit=False)
        self.repo = SQLiteRepository(location+'\data.db')


class APIManager(BaseManager):
    def create_record(self, data, resource, action):
        record_id = self.repo.insert_request(data, resource, action)
        self._create_task(record_id)
        return record_id

    def _create_task(self, record_id):
        self.queue.put(str(record_id))


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
                # TODO: run cli task
                cmd = 'C:\Users\Dmytro_Khanas\projects\dlab\\test.py "{}"'.format(record_id)
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = p.communicate()
                if err:
                    raise Exception(err)
                print(out, err)
                print('from manager run ' + str(record_id))
                self.finish_task(record_id)
            except Exception as e:
                print(e)
                self.process_error(record_id, str(e))

    def finish_task(self, record_id):
        self.queue.task_done()
        self.repo.update_status(record_id, DONE)

    def process_error(self, record_id, message):
        self.repo.update_error(record_id, message)

    def start_task(self):
        record_id = self.queue.get()
        self.repo.update_status(record_id, STARTED)
        return record_id


if __name__ == '__main__':
    m = DaemonManager()
    try:
        m.run()
    except KeyboardInterrupt:
        sys.exit(0)
