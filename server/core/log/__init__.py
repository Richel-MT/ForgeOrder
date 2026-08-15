from threading import Thread
from queue import Queue
from typing import Literal

from .console import getConsoleLogger
from .logger import Logger, setupLogger
from .context import getLogContext


logger: Logger | None = None
dbLoggerThread : Thread | None = None 
dbLoggerQueue : Queue | None = None 

_loggerName : str  = ""
_databaseName : str  = ""
_level: Literal["info", "debug", "warning", "error", "critical", "_MISSING"]  = "_MISSING"


def initLogger(loggerName: str, databaseName: str, level: Literal["info", "debug", "warning", "error", "critical"]):
    global _loggerName, _databaseName, _level

    _loggerName, _databaseName, _level = loggerName, databaseName, level

def getLogger():
    global logger, dbLoggerThread, dbLoggerQueue
    global _loggerName, _databaseName, _level

    if _level == "_MISSING" or _loggerName == "" or _databaseName == "":
        raise ValueError("Logger not initialized. Please call initLogger first.")

    if logger is None or dbLoggerThread is None or dbLoggerQueue is None:
        logger, dbLoggerThread, dbLoggerQueue = setupLogger(_loggerName, _databaseName, _level)

    return logger

def shutdownLogger():
    global logger, dbLoggerThread, dbLoggerQueue

    if logger and dbLoggerThread and dbLoggerQueue:

        dbLoggerQueue.join()

        dbLoggerQueue.put(None)

        dbLoggerThread.join()




        





