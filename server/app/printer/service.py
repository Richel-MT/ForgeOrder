from queue import Queue
from threading import Thread
import uuid
import json
import datetime

from ..db.get_db import get_database
from ..db.main_db import MainDatabase
from .receipt import Receipt
from app.printer import receipt
from .worker import create_print_worker
from  core.log.logger import Logger




class PrintManager:
    def __init__(self, logger: Logger):
        self.queue: Queue
        self.worker_thread : Thread
        self.logger = logger

        self._init()

    def _init(self):
        self.queue, self.worker_thread = create_print_worker(self.logger)

    def new(self, content: Receipt, context: dict = {}, db: MainDatabase | None = None):
        if db is None:
            db = get_database()
            
        id = str(uuid.uuid7())

        content_str = content.render_json()

        context_str = json.dumps(context)

        now = datetime.datetime.now()

        db.print_task.new(id, content_str, now, context_str)

        self.queue.put(id)


        self.logger.info({
            "id": id,
        }, "PRINTER", "PrintTaskCreated")

        return id


    def shutdown(self):
        # self.queue.join()
        self.queue.put(None)

        self.worker_thread.join()



if __name__ == "__main__":
    pm = PrintManager(Logger("fuck"))

    

    pm.new(receipt, {"fuck": "fuck"})


