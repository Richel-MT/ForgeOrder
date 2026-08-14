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

    logger = extensions.getLogContext(extensions.logger, "Main")
    
    logger.debug({
        "version": extensions.version,
        "environment": os.environ["ENV"],
    }, "RuntimeInfo")

    

    # 初始化flask
    app = setupApp()
    
    consoleLogger.info("正在启动HTTP服务...")

    host = extensions.config.get("server.host")
    port = extensions.config.get("server.port")

    logger.info({
            "host": host,
            "port": port,
        },  "StartServer")

    consoleLogger.info(f"启动成功({int((time.time() - initTime) * 1000)}ms)")
    
    if os.environ["ENV"] == "product":

        from waitress import serve

        serve(app, host=host, port=port)

    else:
    
        app.run(
            host=host,
            port=port,
        )


    logger.info('', "ServerStopped")


    shutdown()








    

    