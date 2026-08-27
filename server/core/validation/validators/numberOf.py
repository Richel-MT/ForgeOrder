
from typing import Any, Type

from .base import Validator, ValidationResult
from .range import Range
from .typeOf import TypeOf

class NumberOf(Validator):
    
    def __init__(self, valueType: type[int | float] | None = None):

        self.valueType = valueType

        self._range = Range()

        self._validator = TypeOf(self.valueType) & self._range


    def MinEqual(self, value: int | float):
        if not self.valueType:
            raise ValueError("valueType has already been set. The min and max cannot be specified.")

        self._range.MinEqual(value)

    def Min(self, value: int | float):
        if not self.valueType:
                    raise ValueError("valueType has already been set. The min and max cannot be specified.")

        self._range.Min(value)

    def Max(self, value: int | float):
        if not self.valueType:
            raise ValueError("valueType has already been set. The min and max cannot be specified.")

        self._range.Max(value)
        
    def MaxEqual(self, value: int | float):
        if not self.valueType:
            raise ValueError("valueType has already been set. The min and max cannot be specified.")

        self._range.MaxEqual(value)

    def _validate(self, value: Any, context: Any = None) -> ValidationResult:
        return self._validator._validate(value, context)
    

        
        

        
        


        