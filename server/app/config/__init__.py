from core.config.json_config import JSONConfig
from .schema import CONFIG_ITEMS
from .verify import validateConfig


def setupConfig():

    default = {}

    for item in CONFIG_ITEMS:
        default[item.key] = item.default

    return JSONConfig(
        "data/config.json",
        default,
    )