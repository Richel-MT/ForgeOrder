# 全局对象，供所有脚本使用
from queue import Queue
from threading import Thread
import os

from app.printer.service import PrintManager
from core.auth import AuthManager
from core.config.json_config import JSONConfig
from core.log.logger import Logger
from app.routes.manager import RouteManager
from core.log.context import get_log_context

version: str = "0.0.1"

logger: Logger
db_logger_thread : Thread
db_logger_queue : Queue


auth_manager : AuthManager


config : JSONConfig




local_ip: str = ""


root_dir = os.path.dirname(os.path.abspath(__file__))


route_manager: RouteManager


app_settings: SettingsConnection


print_manager: PrintManager



