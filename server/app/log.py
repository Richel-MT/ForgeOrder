from typing import Callable

from flask import request, g 

from core.log.context import LogContext
from core.log.logger import Logger

class LogContextWithRequestId(LogContext):
    def __init__(self, logger: Logger, category: str, requestId: str, onBeforeLog: Callable):
        super().__init__(logger, category)

        self.requestId = requestId
        self.onBeforeLog = onBeforeLog

    def log(self, msg: str | dict | list , level: int, action: str, requestId: str = ""):
        self.onBeforeLog()

        super().log(msg, level, action, self.requestId)

class RequestLogContext(LogContext):
    def __init__(self, logger: Logger, category: str = ""):
        super().__init__(logger, category)

        if hasattr(g, 'args'):
            args = g.args
        else:
            args = {}
            
        self.requestInfo = {
            "requestId": g.requestId,
            "ip": request.remote_addr,
            "path": request.path,
            "method": request.method,
            "args": args,
        }

        self.requestInfoLogged = False

    def setCategory(self, category: str):
        self.category = category

    def _onBeforeLog(self):
        if not self.requestInfoLogged:
            self.logger.info(self.requestInfo, "REQUEST","RequestInfo", g.requestId)
            self.requestInfoLogged = True

    def log(self, msg: str | dict | list , level: int, action: str, requestId: str = None):
        self._onBeforeLog()

        return super().log(msg, level, action, g.requestId)
        
    def getLogContext(self, category: str):
        return LogContextWithRequestId(self.logger, category, g.requestId, self._onBeforeLog)




