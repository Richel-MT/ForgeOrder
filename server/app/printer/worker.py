import threading
from queue import Queue, Empty
import json
import traceback
import datetime

from escpos.printer import Usb, Network, Win32Raw
from escpos.escpos import Escpos


from app.app_settings.manager import SettingsManager
from core.log.console import get_console_logger
from core.log.context import get_log_context
from core.log.logger import Logger
from app.db.connections import get_database_
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
    c_logger = get_console_logger("printWorker")

    log_ctx = get_log_context(logger, "PRINT_WORKER")

    db = get_database_()
    sm = SettingsManager(db)


    # 初始化连接信息
    connect_info = {}

    connect_info["type"] = sm.get("printer.connection.type")
    if connect_info["type"] == "Network":
        connect_info["ip"] = sm.get("printer.connection.network.ip")
        connect_info["port"] = sm.get("printer.connection.network.port")
        connect_info["timeout"] = sm.get("printer.connection.network.timeout")
    elif connect_info["type"] == "Usb":

        connect_info["vid"] = sm.get("printer.connection.usb.vid")
        connect_info["pid"] = sm.get("printer.connection.usb.pid")

    elif connect_info["type"] == "Win32Raw":
        connect_info["name"] = sm.get("printer.connection.win32.name")

    connect_info["encoding"] = sm.get("printer.encoding")
    connect_info["profile"] = sm.get("printer.profile")


    qr_info = {}
    qr_info["model"] = sm.get("printer.QRCode.model")
    qr_info["native"] = sm.get("printer.QRCode.native")
    qr_info["correction"] = sm.get("printer.QRCode.correction")

    dots = sm.get("printer.dotsPerLine")

    printer: Escpos | None = None
    retry_connect_count = 0

    while True:
        # 从队列中获取任务
        try:
            entry = q.get(timeout=5)
        except Empty:
            # 五秒内没有其他任务
            log_ctx.debug("5秒内没有任务", "DebugMsg")

            if printer is not None:
                log_ctx.debug("关闭打印机连接", "DebugMsg")
                printer.close()
                printer = None

            continue

        if entry is None:
            break

        started_time = datetime.datetime.now()
        db.print_task.update(entry, 1, None, started_time)

        

        log_ctx.debug(f"获取任务 %s" % entry, "DebugMsg")

        # 连接打印机
        if printer is None:
            try:
                printer = connect_printer(connect_info)
            except Exception as e:
                retry_connect_count += 1

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

                if retry_connect_count >= 5:
                    log_ctx.error("", "RetryConnectExhausted")
                    break

                continue

            retry_connect_count = 0

        log_ctx.debug("连接打印机成功", "DebugMsg")
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

        log_ctx.debug("打印任务成功", "DebugMsg")


        log_ctx.info({
            "id": entry,
        }, "PrintTaskFinished")

           

    db.close()

    log_ctx.info("", "StoppedWorker")



        

def create_print_worker(logger: Logger):
    q = Queue()

    thread = threading.Thread(target=print_worker, args=( q, logger), name="PrintWorker")
    thread.daemon = True
    thread.start()

    return q, thread
