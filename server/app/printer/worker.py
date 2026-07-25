import threading
from queue import Queue
import json
import traceback

from app.db.main_db import MainDatabase
from core.log.console import get_console_logger
from core.log.logger import Logger
from app.db.get_db import get_database

def print_worker(q: Queue, logger: Logger):
    c_logger = get_console_logger("printWorker")

    db = get_database()

    while True:
        try:
            entry = q.get()

            if entry is None:
                c_logger.info("打印线程停止")
                break

            print_info = db.print_task.get(entry)
            # print(print_info)
            content = json.loads(print_info["content"])



        except Exception as e:

            logger.error({
                "name": e.__class__.__name__,
                "msg": str(e),
                "traceback": traceback.format_exception(e)
            }, "PRINT_WORKER", "Error")

            continue


    db.close()

        

def create_print_worker( logger: Logger):
    q = Queue()

    thread = threading.Thread(target=print_worker, args=( q, logger), name="PrintWorker")
    thread.daemon = True
    thread.start()

    return q, thread
