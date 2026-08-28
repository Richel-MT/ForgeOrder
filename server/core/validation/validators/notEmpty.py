from typing import Any

from core.validation.exceptions import UnsupportedTypeError

from .base import Validator, ValidationResult
from .._errors import ValidationError

class EmptyError(ValidationError):
    def __str__(self):
        return "The value cannot be empty."

    
class NotEmpty(Validator):
    '''
    不可为空。
    '''
    allowTypes =  None #type: ignore

    def __init__(self, strict: bool = False):
        self.strict = strict 
        # 在严格模式下，传入非str | tuple | list | dict | None的值会抛出UnsupportedTypeError
        # 非严格模式下，会尝试转换


    def _validate(self, value: Any, context: Any = None):

        if not (isinstance(value, (str, tuple, list, dict)) or value is None):
            if self.strict:
                raise UnsupportedTypeError(type(self), (str, tuple, list, dict, None), type(value))

        result = bool(value)

        if not result:
            return ValidationResult(False, EmptyError())
        else:
            return ValidationResult(True)

    def __eq__(self, other):
        return isinstance(other, NotEmpty)

    
