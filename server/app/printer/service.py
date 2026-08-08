from queue import Queue
from threading import Thread

from ..service.print_task import PrintTaskService

from .receipt import Receipt
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

    def new(self, content: Receipt, service: PrintTaskService, context: dict = {}, ):

            
        result = service.create(content, context)

        task_id = result.data

        self.queue.put(task_id)


        self.logger.info({
            "id": task_id,
        }, "PRINTER", "PrintTaskCreated")

        return task_id


    def shutdown(self):
        self.queue.put(None)

        self.worker_thread.join()



if __name__ == "__main__":
    pm = PrintManager(Logger("fuck"))

    

    # pm.new(receipt, {"fuck": "fuck"})


