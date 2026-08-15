import datetime
import queue
import threading
import sqlite3
import os

from .schema import BUFFER_SIZE
from .service import initService
from ..database.database.exceptions import DatabaseError
from ..database.repository.exceptions import RepositoryError
from .console import getConsoleLogger

def writeTextLog(entry):
    now = datetime.datetime.now()

    filePath = f"data/{now.strftime('%Y-%m-%d')}.log"
    
    try:
        with open(filePath, "r") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    
    with open(filePath, "a") as f:
        if content != "":
            f.write('''
服务器无法将日志写入数据库。
{entry}
''')
        else:
            f.write(str(entry))
        

def worker(q: queue.Queue, databaseName: str):
    bufferCount = 0

    # 连接数据库
    database, service = initService(databaseName)
    logger = getConsoleLogger(__name__)

    while True:
        try:
            
            entry = q.get()

            if entry is None:
                q.task_done()
                break


            service.insertLog(*entry)

            bufferCount += 1

            if bufferCount >= BUFFER_SIZE:
                service.commit()
                bufferCount = 0

            q.task_done()
            
        except (DatabaseError, RepositoryError) as e:
            logger.warning(f"数据库错误：{e}")

            try:
                writeTextLog(entry)
            except NameError:
                # entry可能未定义
                pass

        except (KeyboardInterrupt, EOFError):
            break

    service.commit()

    database.close()

def createWorker(databaseName: str):
    q = queue.Queue()

    thread = threading.Thread(target=worker, args=(q, databaseName), name="LogWorker")
    thread.daemon = True
    thread.start()

    return q, thread


        
        