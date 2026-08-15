import logging
import os
import sys
from typing import cast

from app.db.respository import RepositoryManager
from app.service import initService
from app.service.settings import SettingsService
from core.database.database import Database

from app.printer.service import PrintManager
import extensions
from app.config import setupConfig
from core.log.logger import setupLogger
from app.routes.manager import RouteManager
from app.hooks.schema import CLIENT_ERROR
from core.log import getConsoleLogger

from app.cli import createParser, executeCommand
from app.config.validate import validateConfig
from app.exceptions import UserError

consoleLogger= getConsoleLogger("startup")

def initRootUser(reset = False):

    import random
    from app.service import initService, UserService


    password = "".join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=8))

    db, _, service = cast(tuple[Database, None, UserService], initService(extensions.config.get("database.path"), UserService))
    
    try:
        if reset:
            status, rootUser = service.get(username="root")

            

            if status is service.USER.SUCCESS:
                rootUser = cast(dict, rootUser)
                
                rootUserId = rootUser['id']

                service.forceChangePassword(rootUserId, password)

                consoleLogger.info("重置root用户密码：%s" % password)
                return

            else:
                consoleLogger.warning("root用户不存在，无法重置密码")

        service.create("root", password, True, True)


        consoleLogger.info("创建root用户，密码：%s" % password)

        
        extensions.config.set("server.first_start", False)
    finally:
        db.close()

def initLog():
    logger, thread, queue = setupLogger(__name__,
                extensions.config.get("log.database"), # type: ignore
                extensions.config.get("log.level")) #type: ignore

    extensions.logger = logger
    extensions.dbLoggerThread = thread
    extensions.dbLoggerQueue = queue


    # 处理log.ignore_client_error
    if extensions.config.get("log.ignore_client_error"):
        for error in CLIENT_ERROR:
            extensions.logger.setIgnoreAction(error)

def initConfig():
    if not os.path.exists("data"):
            os.makedirs("data")

    # 加载配置文件
    extensions.config = setupConfig()
    


def initArguments():
    parser = createParser()

    args = parser.parse_args()

    if len(sys.argv) > 1:
        consoleLogger.info(f"命令行参数：{' '.join(sys.argv[1:])}")

    return executeCommand(args)


def validateConfigAndSettings():
    # 验证配置项
    try:
        validateConfig()

        db, _, service = initService(extensions.config.get("database.path"), SettingsService)

        try:
            service  = cast(SettingsService, service)

            service._init()
        finally:
            db.close()

    except UserError as e:
            consoleLogger.error(f"启动失败：{e} \n {e.hint}")
            sys.exit(1)

def init():

    consoleLogger.info("正在初始化...")

    # 初始化设置
    initConfig()

    
    # 初始化日志记录器
    initLog()



    # 初始化ArgumentsManager
    extensions.routeManager = RouteManager()


    if extensions.config.get("server.first_start"):
        initRootUser()


    stopRunning = initArguments()

    if stopRunning:
        shutdown()
        sys.exit(0)


    # 初始化数据库的表结构
    db = Database(extensions.config.get("database.path"))
    db.connect()
    
    repos = RepositoryManager(db)
    repos.init()

    # 关闭数据库连接
    db.close()

    validateConfigAndSettings()


    
    extensions.printManager = PrintManager(extensions.logger)

def shutdown():
    # 关闭数据库日志记录器线程
    if extensions.dbLoggerThread is None:
        return
    
    extensions.dbLoggerQueue.join()
    extensions.dbLoggerQueue.put(None)

    extensions.dbLoggerThread.join()



    # 关闭打印服务
    extensions.printManager.shutdown()

    # 关闭日志记录器
    logging.shutdown()