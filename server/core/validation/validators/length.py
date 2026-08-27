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

class LengthIsUnavailableError(Exception):
    
    def __init__(self, valueType: type):
        super().__init__(f"Failed to get the length of {valueType}.")


class Length(Validator):
    '''
    限制值长度在指定范围内。
    允许的类型：str
    '''
    allowTypes = None

    def __init__(self, minValue: int | None, maxValue: int | None):
        self.minValue = minValue
        self.maxValue = maxValue
        
    def _validate(self, value: Any, context: Any = None):

        result = True

        if self.minValue:
            try:
                result = len(value) >= self.minValue
            except ValueError:
                raise LengthIsUnavailableError(type(value))

        if self.maxValue:
            try:
                result = len(value) <= self.maxValue
            except ValueError:
                raise LengthIsUnavailableError(type(value))

        return ValidationResult(
            result,
            None if result else LengthError(self.minValue, self.maxValue)
        )
                                       
