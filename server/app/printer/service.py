from queue import Queue
from threading import Thread

from ..service.printTask import PrintTaskService

from .receipt import Receipt
from .worker import createPrintWorker
from  core.log.logger import Logger




class PrintManager:
    def __init__(self, logger: Logger):
        self.queue: Queue
        self.workerThread : Thread
        self.logger = logger

        self._init()

    def _init(self):
        self.queue, self.workerThread = createPrintWorker(self.logger)

    def new(self, content: Receipt, service: PrintTaskService, context: dict = {}, ):

            
        result = service.create(content, context)

        taskId = result.data

        self.queue.put(taskId)


        self.logger.info({
            "id": taskId,
        }, "PRINTER", "PrintTaskCreated")

        return taskId


    def shutdown(self):
        self.queue.put(None)

        self.workerThread.join()



if __name__ == "__main__":
    pm = PrintManager(Logger("fuck"))

    

    # pm.new(receipt, {"fuck": "fuck"})


