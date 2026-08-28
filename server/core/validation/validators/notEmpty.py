from typing import Any

from .base import Validator, ValidationResult
from .._errors import ValidationError

class EmptyError(ValidationError):
    def __str__(self):
        return "The value cannot be empty."

    
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

    def __eq__(self, other):
        return isinstance(other, NotEmpty)

    
