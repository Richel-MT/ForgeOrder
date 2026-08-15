from core.config.json_config import JSONConfig
from .schema import CONFIG_ITEMS
from .validate import validateConfig


def setupConfig(configPath):

    default = {}

    for item in CONFIG_ITEMS:
        default[item.key] = item.default

    return JSONConfig(
        configPath,
        default,
    )