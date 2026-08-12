# 全局对象，供所有脚本使用
from queue import Queue
from threading import Thread
import os

from app.printer.service import PrintManager
from core.auth import AuthManager
from core.config.json_config import JSONConfig
from core.log.logger import Logger
from app.routes.manager import RouteManager
from core.log.context import getLogContext

version: str = "0.0.1"

logger: Logger
dbLoggerThread : Thread
dbLoggerQueue : Queue


config : JSONConfig


rootDir = os.path.dirname(os.path.abspath(__file__))


routeManager: RouteManager





printManager: PrintManager



