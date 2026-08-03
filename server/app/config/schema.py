import os

from core.validation.field import FieldDefinition
from core.validation.validators import Choices, NotEmpty, Interval, FunctionHandler, AllOf, Open, Closed
from core.validation.base import ValidationResult

    
CONFIG_ITEMS = [
    FieldDefinition("server.host", str, "0.0.0.0", NotEmpty()),
    FieldDefinition("server.port", int, 5000, Interval(1, 65535)),
    FieldDefinition("log.level", str, "info", Choices("debug", "info", "warning", "error", "critical")),
    FieldDefinition("log.database", str, "data/log.db", NotEmpty()),

    FieldDefinition("log.debug_ignore", list, []),
    FieldDefinition("log.ignore_client_error", bool, False),

    FieldDefinition("database.path", str, "data/main.db", NotEmpty()),

    FieldDefinition("auth.available_time", int, 60, Interval(Open(0), None)), # 无上限

    FieldDefinition("server.env", str, "dev", Choices("dev", "product")),
    FieldDefinition("server.first_start", bool, True),

]

CONFIG_PATH = "data/config.json"