from time import sleep

import persistqueue

from dlab_core.infrastructure.repositories import SQLiteRepository, STARTED, DONE

DB_PATH = 'C:\Users\Dmytro_Khanas\projects\dlab'


class Manager(object):
    def __init__(self, location=None):
        if location is None:
            location = DB_PATH
        self.queue = persistqueue.SQLiteQueue(location, auto_commit=False)
        self.repo = SQLiteRepository(location+'\data.db')

    def run(self):
        record_id = self.start_task()
        try:
            # TODO: run cli task
            sleep(5)
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
        print(record_id)
        return record_id


if __name__ == '__main__':
    m = Manager()
    while True:
        m.run()
