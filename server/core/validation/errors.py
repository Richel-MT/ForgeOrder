from dataclasses import dataclass
from typing import Any


class ValidationError:
    msg : str 

    def __init__(self, msg: str = ""):
        self.msg = msg

    def fix(self, property):
        '''
        返回修复好的值
        '''
        return property.default

    def __str__(self) -> str:
        return self.msg



@dataclass
class ValueTypeError(ValidationError):
    expectedType: type | tuple[type]

    def __str__(self) -> str:
        if isinstance(self.expectedType, type):
            return f"The value must be {self.expectedType.__name__} type."
        else:
            return f"The value must be {",".join(map(lambda x: x.__name__, self.expectedType))} type"


