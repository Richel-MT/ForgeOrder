import time
import os

from app.init import init, shutdown
from core.errorHandler.excepthook import install
from core.log import getConsoleLogger
import extensions
from app.setup import setupApp

install()


if __name__ == "__main__":

    consoleLogger= getConsoleLogger("main")
    initTime = time.time()

    init()

    ## 设置环境变量
    os.environ["ENV"] = extensions.config.get("server.env")

    logger = extensions.getLogContext(extensions.logger, "MAIN")
    
    logger.debug(f"ForgeOrder版本：%s" % extensions.version,"DebugMsg")

    

    # 初始化flask
    app = setupApp()
    
    consoleLogger.info("正在启动HTTP服务...")

    host = extensions.config.get("server.host")
    port = extensions.config.get("server.port")

    
    
    if os.environ["ENV"] == "product":
        logger.debug("生产环境运行。", "DebugMsg")

        from waitress import serve

        logger.info({
            "host": host,
            "port": port,
        },  "StartServer")


        consoleLogger.info(f"启动成功({int((time.time() - initTime) * 1000)}ms)")


        serve(app, host=host, port=port)


    else:
        logger.debug("开发环境运行。", "DebugMsg")

        consoleLogger.info(f"启动成功({int((time.time() - initTime) * 1000)}ms)")
        
        app.run(
            host=host,
            port=port,
        )


    logger.info('', "ServerStopped")


    shutdown()








    

    