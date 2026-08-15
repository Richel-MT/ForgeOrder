from typing import Any, Callable

from .base import Validator
from ..base import ValidationResult
from ..errors import *
from ..exceptions import UnsupportedTypeError, UnsupportedValidatorError

class NotEmpty(Validator):
    '''
    不可为空。
    允许的类型：str | None
    '''
    allowTypes = str | dict | list | None #type: ignore

    def _validate(self, value: Any, context: Any = None):
        isError = False

        if value is not None :
            if isinstance(value, str):
                if value.strip() == "":
                    isError = True
            elif isinstance(value, (dict, list)):
                if len(value) == 0:
                    isError = True

                
        else:
            isError = True

        if isError:
            return ValidationResult(False, EmptyError())
        else:
            return ValidationResult(True)


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


class Choices(Validator):
    '''
    限制值只能是指定的选项。
    允许的类型：Any
    '''
    allowTypes = None

    def __init__(self, *choices):
        self.choices = choices
        
    def _validate(self, value: Any, context: Any = None):
        if value in self.choices:
            return ValidationResult(True)
        else:
            return ValidationResult(False, ChoicesError(self.choices))


class FunctionHandler(Validator):
    '''
    自定义验证器。
    允许的类型：Any
    '''
    allowTypes = None

    def __init__(self, func: Callable):
        self.func = func
        
    def _validate(self, value: Any, context: Any = None):
        result = self.func(value)
        
        if isinstance(result, ValidationResult):
            return result   
        else:
            raise UnsupportedValidatorError(self.__class__)
