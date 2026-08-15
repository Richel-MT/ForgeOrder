from typing import Callable, Any
import json
from datetime import datetime

class TypeConvertError(Exception):
    def __init__(self, sourceType : type, targetType: type):
        self.sourceType = sourceType
        self.targetType = targetType

        super().__init__(f"cannot convert type '{sourceType}' to '{targetType}'")

class TypeConverterManager:
    def __init__(self):
        self.converters: dict[ tuple[type, type], Callable] = {}
    def registerConverter(self, sourceType: type, targetType: type, func: Callable):
        self.converters[(sourceType, targetType)] = func

    def convert(self, value: Any, targetType: type):
        sourceType = type(value)

        if isinstance(value, targetType):
            # 类型一致
            return value

        converter = self.converters.get((sourceType, targetType), None)

        if converter:
            return converter(value)
        else:
            raise TypeConvertError(value, targetType)


converter = TypeConverterManager()

converter.registerConverter(str, int, int)
converter.registerConverter(int, str, str)

converter.registerConverter(str, bool, lambda x: x == "1")
converter.registerConverter(bool, str, lambda x: "1" if x else "0")

converter.registerConverter(str, list, lambda x: json.loads(x))
converter.registerConverter(list, str, lambda x: json.dumps(x))

converter.registerConverter(str, dict, lambda x: json.loads(x))
converter.registerConverter(dict, str, lambda x: json.dumps(x))

converter.registerConverter(datetime, str, lambda x: x.isoformat())
converter.registerConverter(str, datetime, lambda x: datetime.fromisoformat(x))


