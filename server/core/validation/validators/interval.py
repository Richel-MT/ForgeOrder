from dataclasses import dataclass
from typing import Any

from .base import Validator, ValidationResult
from ..errors import ValidationError


@dataclass(frozen=True)
class Boundary:
    value: float | int | None
    inclusive: bool

    def symbolLeft(self):
        return "(" if self.inclusive else "["
    
    def symbolRight(self):
        return ")" if self.inclusive else "]"
       
def Open(value):
    return Boundary(value, False)

def Closed(value):
    return Boundary(value, True)

@dataclass
class IntervalError(ValidationError):
    interval: 'Interval'

    def __str__(self):
        return f"Value must be in {self.interval}"

class Interval(Validator):
    '''
    限制值在一个区间内。
    允许的类型：float | int
    '''
    allowTypes = float | int #type: ignore

    @staticmethod
    def _normalize(value):
        if value is None:
            return Boundary(None, False) 
        if isinstance(value, (int, float)):
            return Boundary(value, True)
        if isinstance(value, Boundary):
            return value
        
        raise UnsupportedTypeError(Interval, float | int, type(value)) #type: ignore
    


    def __init__(self, minValue: Boundary | None | int | float , maxValue: Boundary | None | int | float):
        
        self.minValue = self._normalize(minValue)
        self.maxValue = self._normalize(maxValue)


        
    def _validate(self, value: Any, context: Any = None):
        if self.minValue.value is not None:
            if self.minValue.inclusive and value >= self.minValue.value:
                pass
            elif not self.minValue.inclusive and value > self.minValue.value:
                pass
            else:
                return ValidationResult(False, IntervalError(self))
            
            
        if self.maxValue.value is not None:
            if self.maxValue.inclusive and value <= self.maxValue.value:
                pass
            elif not self.maxValue.inclusive and value < self.maxValue.value:
                pass
            else:
                return ValidationResult(False, self)
            
        return ValidationResult(True)
    
    def __str__(self):
        if self.minValue.value is None:
            minValue = "-∞"
        else:
            minValue = self.minValue.value

        if self.maxValue.value is None:
            maxValue = "+∞"
        else:
            maxValue = self.maxValue.value
            
        return f"{self.minValue.symbolLeft()}{minValue},{maxValue}{self.maxValue.symbolRight()}"
