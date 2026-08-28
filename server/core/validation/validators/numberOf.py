
from typing import Any, Type

from .base import Validator, ValidationResult
from .range import Range
from .typeOf import TypeOf

class NumberOf(Validator):
    
    def __init__(self, valueType: type[int | float] | None = None):

        self.valueType = valueType

        self._range = Range()

    def _checkValue(self, value: int | float):
        if not self.valueType:
            raise ValueError("valueType has already been set. The min and max cannot be specified.")

        if isinstance(value, int):
            self.valueType = int
        else:
            self.valueType = float
        


    def MinEqual(self, value: int | float):
        self._checkValue(value)
             
        self._range.MinEqual(value)

    def Min(self, value: int | float):
        self._checkValue(value)

        self._range.Min(value)

    def Max(self, value: int | float):
        self._checkValue(value)
        
        self._range.Max(value)
        
    def MaxEqual(self, value: int | float):
        self._checkValue(value)

        self._range.MaxEqual(value)

    def _validate(self, value: Any, context: Any = None) -> ValidationResult:
        result = TypeOf(self.valueType)(value, context)

        if not result.success:
            return result

        return self._range(value, context)


    def mergeAnd(self, other: NumberOf):

        # 原本的变量名是newType
        mewType = float # Bang Dream! MewType

        if self.valueType == int or other.valueType == int:
            mewType = int


        newRange = self._range.mergeAnd(other._range)

        newValidator = NumberOf()

        newValidator.valueType = mewType
        newValidator._range = newRange

        return newValidator

    def __eq__(self, other):
        return isinstance(other, NumberOf) and self.valueType == other.valueType and self._range == other._range
         
    

        
        

        
        


        