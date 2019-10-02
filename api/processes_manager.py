from threading import Thread
from time import sleep

import persistqueue

from dlab_core.infrastructure.repositories import SQLiteRepository, STARTED, DONE

DB_PATH = 'C:\Users\Dmytro_Khanas\projects\dlab'
num_worker_threads = 2


class Manager(object):
    def __init__(self, location=None):
        if location is None:
            location = DB_PATH
        self.queue = persistqueue.FIFOSQLiteQueue(location, multithreading=True, auto_commit=False)
        self.repo = SQLiteRepository(location+'\data.db')
        for i in range(num_worker_threads):
            t = Thread(target=self.run)
            t.daemon = True
            t.start()

    def run(self):
        while True:
            record_id = self.start_task()
            try:
                # TODO: run cli task
                sleep(10)
                # print(type(record_id))
                # if record_id == '238':
                #     raise Exception('test error')
                # print('from manager run ' + str(record_id))
                self.finish_task(record_id)
            except Exception as e:
                self.process_error(record_id, str(e))

    def create_record(self, data):
        record_id = self.repo.insert_request(data)
        self._create_task(record_id)
        return record_id

    def _create_task(self, record_id):
        self.queue.put(str(record_id))

    def finish_task(self, record_id):
        self.queue.task_done()
        self.repo.update_status(record_id, DONE)

    def process_error(self, record_id, message):
        self.repo.update_error(record_id, message)

    def start_task(self):
        record_id = self.queue.get()
        self.repo.update_status(record_id, STARTED)
        print('from manager start_task ' + str(record_id))
        return record_id


if __name__ == '__main__':
    m = Manager()
    m.run()
