import threading
from queue import Queue, Empty
import json
import traceback
import datetime

from escpos.printer import Usb, Network, Win32Raw
from escpos.escpos import Escpos


from app.db.respository import RepositoryManager
from app.service import SettingsService
from core.log.console import getConsoleLogger
from core.log.context import getLogContext
from core.log.logger import Logger
from app.db.connections import getDatabase_
from core.db.exceptions import NotFoundError
from .renderer import Renderer


def connect_printer(connect_info: dict) -> Escpos: #type: ignore
    if connect_info["type"] == "Network":
        return Network(connect_info["ip"], connect_info["port"], connect_info["timeout"], profile=connect_info["profile"], encoding=connect_info["encoding"])
    elif connect_info["type"] == "Usb":
        return Usb(connect_info["vid"], connect_info["pid"], encoding=connect_info["encoding"], profile=connect_info["profile"])
    elif connect_info["type"] == "Win32Raw":
        return Win32Raw(connect_info["name"], profile=connect_info["profile"], encoding=connect_info["encoding"])


def print_task(commands: list, printer: Escpos, qr_info: dict, dots: int):
    renderer = Renderer(printer, qr_info)

    renderer.render(commands, dots)

    printer.cut()


def print_worker(q: Queue, logger: Logger):
    c_logger = getConsoleLogger("printWorker")

    log_ctx = getLogContext(logger, "PrinterWorker")

    db = getDatabase_()
    db.connect()

    repos = RepositoryManager(db)
    settings_service = SettingsService(repos)


    # 初始化连接信息
    connect_info = {}

    connect_info["type"] = settings_service.get("printer.connection.type")
    if connect_info["type"] == "Network":
        connect_info["ip"] = settings_service.get("printer.connection.network.ip")
        connect_info["port"] = settings_service.get("printer.connection.network.port")
        connect_info["timeout"] = settings_service.get("printer.connection.network.timeout")
    elif connect_info["type"] == "Usb":

        connect_info["vid"] = settings_service.get("printer.connection.usb.vid")
        connect_info["pid"] = settings_service.get("printer.connection.usb.pid")

    elif connect_info["type"] == "Win32Raw":
        connect_info["name"] = settings_service.get("printer.connection.win32.name")

    connect_info["encoding"] = settings_service.get("printer.encoding")
    connect_info["profile"] = settings_service.get("printer.profile")


    qr_info = {}
    qr_info["model"] = settings_service.get("printer.QRCode.model")
    qr_info["native"] = settings_service.get("printer.QRCode.native")
    qr_info["correction"] = settings_service.get("printer.QRCode.correction")

    dots = settings_service.get("printer.dotsPerLine")

    printer: Escpos | None = None
    retry_connect_count = 0

    log_ctx.info({
        "connect_info": connect_info,
        "qr_info": qr_info,
    }, "WorkerStarted")

    while True:
        # 从队列中获取任务
        try:
            entry = q.get(timeout=5)
        except Empty:
            # 五秒内没有其他任务

            if printer is not None:
                log_ctx.debug({"message":
                               "Printer connection closed because no print task was received within 5s."}, "ClosePrinterConnection")
                printer.close()
                printer = None

            continue

        if entry is None:
            break

        started_time = datetime.datetime.now()

        


        # 连接打印机
        if printer is None:
            try:
                printer = connect_printer(connect_info)

                log_ctx.debug({
                    "message": "Connected printer"
                }, "ConnectPrinter")
            except Exception as e:

                # 重试次数加1
                retry_connect_count += 1

                # 记录本次的连接错误信息
                log_ctx.warning({
                    "id": entry,
                    "error": {
                        "name": e.__class__.__name__,
                        "msg": str(e),
                        "traceback": traceback.format_exception(e)
                    }
                }, "ConnectError")

                now = datetime.datetime.now()
                db.print_task.update(entry, 3, "PrinterConnectError", started_time, now)

                # 重试次数超过5词，跳出本次循环
                if retry_connect_count >= 5:
                    log_ctx.error("", "RetryConnectExhausted")
                    break

    
                # 重试连接打印机
                continue

            retry_connect_count = 0

        # 读取设置
        try:
            print_info = db.print_task.get(entry)
            content = json.loads(print_info["content"])
        except NotFoundError:
            log_ctx.warning({
                "id": entry,
            }, "NotFoundTask")

            now = datetime.datetime.now()
            db.print_task.update(entry, 3, "NotFoundTask", started_time, now)
            
            continue

        except json.JSONDecodeError as e:
            log_ctx.warning({
                "id": entry,
                "error": str(e)
            }, "InvalidTaskContent")

            now = datetime.datetime.now()
            db.print_task.update(entry, 3, "InvalidTaskContent", started_time, now)

            
            continue

        


        # 打印任务
        try:
            print_task(content["commands"], printer, qr_info, dots)
        except Exception as e:
            log_ctx.warning({
                "id": entry,
                "error": {
                    "name": e.__class__.__name__,
                    "msg": str(e),
                    "traceback": traceback.format_exception(e)
                }
            }, "PrintTaskError")
            now = datetime.datetime.now()
            db.print_task.update(entry, 3, "PrintTaskError", started_time, now)

            printer.close()
            printer = None

            continue

        now = datetime.datetime.now()
        db.print_task.update(entry, 2, None, started_time, now)


        log_ctx.info({
            "id": entry,
        }, "PrintTaskFinished")

    db.close()       

    log_ctx.info("", "WorkerStopped")

    



        

def create_print_worker(logger: Logger):
    q = Queue()

    thread = threading.Thread(target=print_worker, args=( q, logger), name="PrintWorker")
    thread.daemon = True
    thread.start()

    return q, thread
