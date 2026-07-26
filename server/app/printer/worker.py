import threading
from queue import Queue, Empty
import json
import traceback
import datetime

from escpos.printer import Usb, Network, Win32Raw
from escpos.escpos import Escpos
import win32print

from app.db.main_db import MainDatabase
from app.app_settings.manager import SettingsManager
from core.log.console import get_console_logger
from core.log.context import get_log_context
from core.log.logger import Logger
from app.db.get_db import get_database
from core.db.exceptions import NotFoundError


def connect_printer(connect_info: dict) -> Escpos: #type: ignore
    if connect_info["type"] == "Network":
        return Network(connect_info["ip"], connect_info["port"], connect_info["timeout"])
    elif connect_info["type"] == "Usb":
        return Usb(connect_info["vid"], connect_info["pid"])
    elif connect_info["type"] == "Win32Raw":
        return Win32Raw(connect_info["name"])

def check_printer_status(printer_name):
    try:
        h_printer = win32print.OpenPrinter(printer_name)
        # 获取打印机信息 (索引2对应 PRINTER_INFO_2)
        printer_info = win32print.GetPrinter(h_printer, 2)
        win32print.ClosePrinter(h_printer)

        # 检查离线标志位 (PRINTER_ATTRIBUTE_WORK_OFFLINE = 0x00000400)
        if printer_info['Attributes'] & 0x00000400:
            print(f"打印机 '{printer_name}' 处于离线状态。")
            return False

            
        return True
    except Exception as e:
        return False


def print_text(printer: Escpos, cmd_info :dict):
    args = cmd_info["style"].copy()

    if "font" in args:
        args["font"] = args["font"].lower()

    if "scale" in args:
        args["width"] = args["scale"][0]
        args["height"] = args["scale"][1]
        del args["scale"]

        args["custom_size"] = True
    
    printer.set(**args)

    if cmd_info["newline"]:
        printer.textln(cmd_info["text"])
    else:
        printer.text(cmd_info["text"])

def print_qr(printer: Escpos, cmd_info :dict):
    pass


def print_task(commands: list, printer: Escpos):
    for command in commands:

        match command["type"]:
            case "text":
                print_text(printer, command["value"])

            case "qr_code":
                args = command["value"].copy()
                del args["content"]

                printer.qr(command["value"]["content"], **args)


    printer.cut(mode="FULL")


def print_worker(q: Queue, logger: Logger):
    c_logger = get_console_logger("printWorker")

    log_ctx = get_log_context(logger, "PRINT_WORKER")

    db = get_database()
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
            print_task(content["commands"], printer)
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
            continue

        now = datetime.datetime.now()
        db.print_task.update(entry, 2, None, started_time, now)

        log_ctx.debug("打印任务成功", "DebugMsg")


        log_ctx.info({
            "id": entry,
        }, "PrintTaskFinished")

           

    db.close()

    log_ctx.info("", "StoppedWorker")



        

def create_print_worker( logger: Logger):
    q = Queue()

    thread = threading.Thread(target=print_worker, args=( q, logger), name="PrintWorker")
    thread.daemon = True
    thread.start()

    return q, thread
