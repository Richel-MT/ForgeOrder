from ..base import ValidationResult
from typing import Any, TYPE_CHECKING
from ..exceptions import UnsupportedTypeError

if TYPE_CHECKING:
    from .logical import AllOf, AnyOf, Not

class Validator:
    allowTypes : type | None = None # None 表示接收任意类型

    def validate(self, value: Any = None, context: Any = None) -> ValidationResult:
        if self.allowTypes is None or isinstance(value, self.allowTypes):

            result =  self._validate(value, context)
            
            return ValidationResult(result.success, result.error)
        else:
            # return VerifyResult(False, ValueTypeError(self.allow_types))
        
            raise UnsupportedTypeError(type(self), self.allowTypes, type(value))
        
    def _validate(self, value: Any, context: Any = None) -> ValidationResult: #type: ignore
        pass

    def __call__(self, value: Any) -> ValidationResult:
        return self.validate(value)

    def __and__(self, other: 'Validator') -> 'AllOf':
        from .logical import AllOf
        return AllOf(self, other)

    def __or__(self, other: 'Validator') -> 'AnyOf':
        from .logical import AnyOf
        return AnyOf(self, other)

    def __invert__(self) -> 'Not':
        from .logical import Not
        return Not(self)

    def bind(self, value: Any) -> 'ValidatorWithValue':
        return ValidatorWithValue(self, value)

class ValidatorWithValue(Validator):

    def __init__(self, validator: Validator, value: Any):
        self.validator = validator
        self.value = value

    def validate(self, value = None, context = None) -> ValidationResult:
        if value is not None:
            raise ValueError("The value must be None when using 'ValidatorWithValue'.")
        
        return self.validator.validate(self.value, context)