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
from .renderer import Renderer


def connectPrinter(connectInfo: dict) -> Escpos: #type: ignore
    if connectInfo["type"] == "Network":
        return Network(connectInfo["ip"], connectInfo["port"], connectInfo["timeout"], profile=connectInfo["profile"], encoding=connectInfo["encoding"])
    elif connectInfo["type"] == "Usb":
        return Usb(connectInfo["vid"], connectInfo["pid"], encoding=connectInfo["encoding"], profile=connectInfo["profile"])
    elif connectInfo["type"] == "Win32Raw":
        return Win32Raw(connectInfo["name"], profile=connectInfo["profile"], encoding=connectInfo["encoding"])


def printTask(commands: list, printer: Escpos, qrInfo: dict, dots: int):
    renderer = Renderer(printer, qrInfo)

    renderer.render(commands, dots)

    printer.cut()


def printWorker(q: Queue, logger: Logger):

    logContext = getLogContext(logger, "PrinterWorker")

    db = getDatabase_()
    db.connect()

    repos = RepositoryManager(db)
    settingsService = SettingsService(repos)


    # 初始化连接信息
    connectInfo = {}

    connectInfo["type"] = settingsService.get("printer.connection.type")
    if connectInfo["type"] == "Network":
        connectInfo["ip"] = settingsService.get("printer.connection.network.ip")
        connectInfo["port"] = settingsService.get("printer.connection.network.port")
        connectInfo["timeout"] = settingsService.get("printer.connection.network.timeout")
    elif connectInfo["type"] == "Usb":

        connectInfo["vid"] = settingsService.get("printer.connection.usb.vid")
        connectInfo["pid"] = settingsService.get("printer.connection.usb.pid")

    elif connectInfo["type"] == "Win32Raw":
        connectInfo["name"] = settingsService.get("printer.connection.win32.name")

    connectInfo["encoding"] = settingsService.get("printer.encoding")
    connectInfo["profile"] = settingsService.get("printer.profile")


    qrInfo = {}
    qrInfo["model"] = settingsService.get("printer.QRCode.model")
    qrInfo["native"] = settingsService.get("printer.QRCode.native")
    qrInfo["correction"] = settingsService.get("printer.QRCode.correction")

    dots = settingsService.get("printer.dotsPerLine")

    printer: Escpos | None = None
    retryConnectCount = 0

    logContext.info({
        "connectInfo": connectInfo,
        "qrInfo": qrInfo,
    }, "WorkerStarted")

    while True:
        # 从队列中获取任务
        try:
            entry = q.get(timeout=5)
        except Empty:
            # 五秒内没有其他任务

            if printer is not None:
                logContext.debug({"message":
                               "Printer connection closed because no print task was received within 5s."}, "ClosePrinterConnection")
                printer.close()
                printer = None

            continue

        if entry is None:
            break

        startTime = datetime.datetime.now()

        


        # 连接打印机
        if printer is None:
            try:
                printer = connectPrinter(connectInfo)

                logContext.debug({
                    "message": "Connected printer"
                }, "ConnectPrinter")
            except Exception as e:

                # 重试次数加1
                retryConnectCount += 1

                # 记录本次的连接错误信息
                logContext.warning({
                    "id": entry,
                    "error": {
                        "name": e.__class__.__name__,
                        "msg": str(e),
                        "traceback": traceback.format_exception(e)
                    }
                }, "ConnectError")

                now = datetime.datetime.now()
                db.print_task.update(entry, 3, "PrinterConnectError", startTime, now)

                # 重试次数超过5词，跳出本次循环
                if retryConnectCount >= 5:
                    logContext.error("", "RetryConnectExhausted")
                    break

    
                # 重试连接打印机
                continue

            retryConnectCount = 0

        # 读取设置
        try:
            printInfo = db.print_task.get(entry)
            content = json.loads(printInfo["content"])
        except NotFoundError:
            logContext.warning({
                "id": entry,
            }, "NotFoundTask")

            now = datetime.datetime.now()
            db.print_task.update(entry, 3, "NotFoundTask", startTime, now)
            
            continue

        except json.JSONDecodeError as e:
            logContext.warning({
                "id": entry,
                "error": str(e)
            }, "InvalidTaskContent")

            now = datetime.datetime.now()
            db.print_task.update(entry, 3, "InvalidTaskContent", startTime, now)

            
            continue

        


        # 打印任务
        try:
            printTask(content["commands"], printer, qrInfo, dots)
        except Exception as e:
            logContext.warning({
                "id": entry,
                "error": {
                    "name": e.__class__.__name__,
                    "msg": str(e),
                    "traceback": traceback.format_exception(e)
                }
            }, "PrintTaskError")
            now = datetime.datetime.now()
            db.print_task.update(entry, 3, "PrintTaskError", startTime, now)

            printer.close()
            printer = None

            continue

        now = datetime.datetime.now()
        db.print_task.update(entry, 2, None, startTime, now)


        logContext.info({
            "id": entry,
        }, "PrintTaskFinished")

    db.close()       

    logContext.info("", "WorkerStopped")

    



        

def createPrintWorker(logger: Logger):
    q = Queue()

    thread = threading.Thread(target=printWorker, args=( q, logger), name="PrintWorker")
    thread.daemon = True
    thread.start()

    return q, thread
