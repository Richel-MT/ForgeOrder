from ..base import ValidationResult
from typing import Any

class Validator:
    allow_types : type | None = None # None 表示接收任意类型

    def validate(self, value: Any = None) -> ValidationResult:
        if self.allow_types is None or isinstance(value, self.allow_types):

            result =  self._validate(value)
            
            return ValidationResult(result.success, result.error)
        else:
            # return VerifyResult(False, ValueTypeError(self.allow_types))
        
            raise UnsupportedTypeError(self, self.allow_types, type(value)) #type: ignore
        
    def _validate(self, value: Any) -> ValidationResult: #type: ignore
        pass

    def __call__(self, value: Any) -> ValidationResult:
        return self.validate(value)

    def bind(self, value: Any) -> 'ValidatorWithValue':
        return ValidatorWithValue(self, value)

class ValidatorWithValue(Validator):

    def __init__(self, validator: Validator, value: Any):
        self.validator = validator
        self.value = value

    def validate(self, value = None) -> ValidationResult:
        if value is not None:
            raise ValueError("The value must be None when using 'ValidatorWithValue'.")
        
        return self.validator.validate(self.value)