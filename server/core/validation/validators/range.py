from dataclasses import dataclass
from typing import Any

from .base import Validator, ValidationResult
from .._errors import ValidationError, ValueTypeError



@dataclass
class RangeError(ValidationError):
    _range: 'Range'

    def __str__(self):
        return f"Value must be in {self._range}"

class UncomparableValueError(Exception):

    def __init__(self, valueType: type):

        super().__init__(f"The type of value {valueType} is not compareable.")

class Range(Validator):
    '''
    限制值在一个区间内。
    允许的类型：任何支持>、<、>=、<=运算符的对象
    '''
    allowTypes = None


    def __init__(self):
        
        self.minValue = None
        self.isMinEqual = None
    
        self.maxValue = None
        self.isMaxEqual = None


    def Min(self, value: Any):
        self.minValue = value
        self.isMinEqual = False

        return self

    def Max(self, value: Any):
        self.maxValue = value
        self.isMaxEqual = False

        return self

    def MinEqual(self, value: Any):
        self.minValue = value
        self.isMinEqual = True

        return self

    def MaxEqual(self, value: Any):
        self.maxValue = value
        self.isMaxEqual = True
        
    def _validate(self, value: Any, context: Any = None):
        if self.minValue:

            try:
                if self.isMinEqual:
                    if value < self.minValue.value:
                        return ValidationResult(False, RangeError(self))
                else:
                    if value <= self.minValue.value:
                        return ValidationResult(False, RangeError(self))

            except TypeError:
                raise UncomparableValueError(type(value))

        if self.maxValue:
            try:
                if self.isMaxEqual:
                    if value > self.maxValue.value:
                        return ValidationResult(False, RangeError(self))
                else:
                    if value <= self.maxValue.value:
                        return ValidationResult(False, RangeError(self))

            except TypeError:
                raise UncomparableValueError(type(value))
    
    
        return ValidationResult(True)
    
    def __str__(self):
        if self.minValue and self.maxValue:
            return f"{self.minValue} {"<=" if self.isMinEqual else "<"} value {"<=" if self.isMaxEqual else "<"} {self.maxValue}"
        elif self.minValue:
            return f"value {">=" if self.isMinEqual else ">"} {self.minValue}"

        else:
            return f"value {"<=" if self.isMaxEqual else "<"} {self.maxValue}"
    
