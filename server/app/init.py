import logging
import os
import sys

from app.db.respository import RepositoryManager
from app.service.settings import SettingsService
from core.database.database import Database

from app.printer.service import PrintManager
import extensions
from app.config import setup_config
from core.log.logger import setup_logger
from app.routes.manager import RouteManager
from app.hooks.schema import CLIENT_ERROR
from app.db.main_db import MainDatabase
from core.log import get_console_logger

from app.cli import create_parser, execute_command
from app.config.verify import verify_config
from app.exceptions import UserError

console_logger= get_console_logger("startup")

def init_root_user(reset = False):

    import random
    from werkzeug.security import generate_password_hash
    from app.db.main_db import MainDatabase


    password = "".join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=8))
    password_hash = generate_password_hash(password)

    database = MainDatabase(extensions.config.get("database.path"))

    if reset:
        root_user = database.users.get_from_username("root")
        if root_user:
            root_user_id = root_user['id']

            database.users.change_pasword(root_user_id, password_hash)

            console_logger.info("重置root用户密码：%s" % password)
            return

        else:
            console_logger.warning("root用户不存在，无法重置密码")

    database.users.new_s("root", password_hash, True, True)
    console_logger.info("创建root用户，密码：%s" % password)
    database.close()

    
    
    extensions.config.set("server.first_start", False)

def init_log():
    logger, thread, queue = setup_logger(__name__,
                extensions.config.get("log.database"), # type: ignore
                extensions.config.get("log.level")) #type: ignore

    extensions.logger = logger
    extensions.db_logger_thread = thread
    extensions.db_logger_queue = queue


    # 处理log.ignore_client_error
    if extensions.config.get("log.ignore_client_error"):
        for error in CLIENT_ERROR:
            extensions.logger.setIgnoreAction(error)

def init_config():
    if not os.path.exists("data"):
            os.makedirs("data")

    # 加载配置文件
    extensions.config = setup_config()
    


def init_args():
    parser = create_parser()

    args = parser.parse_args()

    if len(sys.argv) > 1:
        console_logger.info(f"命令行参数：{' '.join(sys.argv[1:])}")

    return execute_command(args)


def verify_config_and_settings(repos: RepositoryManager):
    # 验证配置项
    try:
        verify_config()



        service = SettingsService(repos)

        service._init()

        return service

    except UserError as e:
            console_logger.error(f"启动失败：{e} \n {e.hint}")
            sys.exit(1)

def init():

    console_logger.info("正在初始化...")

    # 初始化设置
    init_config()

    
    # 初始化日志记录器
    init_log()

    # 初始化数据库表
    db = Database(extensions.config.get("database.path"))
    db.connect()
    
    repos = RepositoryManager(db)
    repos.init()

    

    # 取本地ip（将弃用）
    extensions.local_ip = "will be deprecated"


    # 初始化ArgumentsManager
    extensions.route_manager = RouteManager()


    if extensions.config.get("server.first_start"):
        init_root_user()


    stop_running = init_args()

    if stop_running:
        shutdown()
        sys.exit(0)


    settings_service = verify_config_and_settings(repos)


    extensions.app_settings = settings_service
    
    extensions.print_manager = PrintManager(extensions.logger)

def shutdown():
    # 关闭数据库日志记录器线程
    if extensions.db_logger_thread is None:
        return
    
    extensions.db_logger_queue.join()
    extensions.db_logger_queue.put(None)

    extensions.db_logger_thread.join()

    # 关闭全局的AppSettings数据库连接
    extensions.app_settings.db.close()

    # 关闭打印服务
    extensions.print_manager.shutdown()

    # 关闭日志记录器
    logging.shutdown()
