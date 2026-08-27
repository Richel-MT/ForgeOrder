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
    expectedType: type

    def __str__(self) -> str:
        return f"The handler only allows {self.expectedType} type."


