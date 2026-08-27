from typing import Any
from dataclasses import dataclass

from .base import Validator, ValidationResult
from ..errors import ValidationError

@dataclass
class LengthError(ValidationError):
    min: int | None = None
    max: int | None = None

    def __str__(self) -> str:
        return f"The length of value must be between {self.min} and {self.max}."


class Length(Validator):
    '''
    限制值长度在指定范围内。
    允许的类型：str
    '''
    allowTypes = str | dict | list | None #type: ignore

    def __init__(self, minValue: int | None, maxValue: int | None):
        self.minValue = minValue
        self.maxValue = maxValue
        
    def _validate(self, value: Any, context: Any = None):
        if not isinstance(value, str):
            return ValidationResult(False, LengthError(self.minValue, self.maxValue))

        if self.minValue is None or self.minValue <= len(value) and self.maxValue is None or self.maxValue >= len(value):
            return ValidationResult(True)
        else:
            return  ValidationResult(False, LengthError(self.minValue, self.maxValue))
