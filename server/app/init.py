import logging
import os
import sys
from typing import cast

from app.db.respository import RepositoryManager
from app.service import init_service
from app.service.settings import SettingsService
from core.database.database import Database

from app.printer.service import PrintManager
import extensions
from app.config import setupConfig
from core.log.logger import setup_logger
from app.routes.manager import RouteManager
from app.hooks.schema import CLIENT_ERROR
from core.log import getConsoleLogger

from app.cli import createParser, executeCommand
from app.config.verify import validateConfig
from app.exceptions import UserError

console_logger= getConsoleLogger("startup")

def init_root_user(reset = False):

    import random
    from app.service import init_service, UserService


    password = "".join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=8))

    db, _, service = cast(tuple[Database, None, UserService], init_service(extensions.config.get("database.path"), UserService))
    
    try:
        if reset:
            status, root_user = service.get(username="root")

            

            if status is service.USER.SUCCESS:
                root_user = cast(dict, root_user)
                
                root_user_id = root_user['id']

                service.change_password_force(root_user_id, password)

                console_logger.info("重置root用户密码：%s" % password)
                return

            else:
                console_logger.warning("root用户不存在，无法重置密码")

        service.create("root", password, True, True)


        console_logger.info("创建root用户，密码：%s" % password)

        
        extensions.config.set("server.first_start", False)
    finally:
        db.close()

def init_log():
    logger, thread, queue = setup_logger(__name__,
                extensions.config.get("log.database"), # type: ignore
                extensions.config.get("log.level")) #type: ignore

    extensions.logger = logger
    extensions.dbLoggerThread = thread
    extensions.db_logger_queue = queue


    # 处理log.ignore_client_error
    if extensions.config.get("log.ignore_client_error"):
        for error in CLIENT_ERROR:
            extensions.logger.setIgnoreAction(error)

def init_config():
    if not os.path.exists("data"):
            os.makedirs("data")

    # 加载配置文件
    extensions.config = setupConfig()
    


def init_args():
    parser = createParser()

    args = parser.parse_args()

    if len(sys.argv) > 1:
        console_logger.info(f"命令行参数：{' '.join(sys.argv[1:])}")

    return executeCommand(args)


def verify_config_and_settings():
    # 验证配置项
    try:
        validateConfig()

        db, _, service = init_service(extensions.config.get("database.path"), SettingsService)

        try:
            service  = cast(SettingsService, service)

            service._init()
        finally:
            db.close()

    except UserError as e:
            console_logger.error(f"启动失败：{e} \n {e.hint}")
            sys.exit(1)

def init():

    console_logger.info("正在初始化...")

    # 初始化设置
    init_config()

    
    # 初始化日志记录器
    init_log()



    # 初始化ArgumentsManager
    extensions.routeManager = RouteManager()


    if extensions.config.get("server.first_start"):
        init_root_user()


    stop_running = init_args()

    if stop_running:
        shutdown()
        sys.exit(0)


    # 初始化数据库

    db = Database(extensions.config.get("database.path"))
    db.connect()
    
    repos = RepositoryManager(db)
    repos.init()
    db.close()

    verify_config_and_settings()


    
    extensions.printManager = PrintManager(extensions.logger)

def shutdown():
    # 关闭数据库日志记录器线程
    if extensions.dbLoggerThread is None:
        return
    
    extensions.db_logger_queue.join()
    extensions.db_logger_queue.put(None)

    extensions.dbLoggerThread.join()



    # 关闭打印服务
    extensions.printManager.shutdown()

    # 关闭日志记录器
    logging.shutdown()