
import sys
import time

from core.log import getConsoleLogger
from app.config import config, CONFIG


def _fixConfig():
    from app.config.schema import CONFIG_ITEMS
    # from core.config.validation import 
    from app.config.validate import validateConfig

    logger = getConsoleLogger("fix")

    errors = validateConfig(config.getConfigInstance(), True)

    if not errors:
        logger.info("未找到配置项问题")
        return

    logger.info(f"找到了{len(errors)}个配置问题")
    

    for key, result in errors.items():
        if not (result.can_fix and result.error is not None):
            logger.warning(f"无法修复配置项{key}")
        else:
            
            property = [item for item in CONFIG_ITEMS if item.key == key][0]

            fixedValue = result.error.fix(property)
            logger.info(f"已修复{key}(默认值：{fixedValue})")


            config.set(key, fixedValue)
        


def fix(exit: bool = True):
    logger = getConsoleLogger("fix")
    startTime = time.time()

    
    _fixConfig()

    endTime = time.time()

    logger.info(f"修复完成({int(1000 * (endTime - startTime))}ms)")
    

        

