from typing import Any
from dataclasses import dataclass

from .base import Validator, ValidationResult
from .._errors import ValidationError, ValueTypeError


class AnyOfError(ValidationError):  
    children: list[ValidationError]

    def __init__(self, *children):
        self.children = list(children)

    def __str__(self) -> str:
        return "The value must match any of the following validators: " + ", ".join([str(child) for child in self.children])



class AllOfError(ValidationError):
    children: list[ValidationError]

    def __init__(self, *children):
        self.children = list(children)

    def __str__(self) -> str:
        return "The value must match all of the following validators: " + ", ".join([str(child) for child in self.children])

@dataclass
class AllOfAssertError(ValidationError):
    children: ValidationError

    def __str__(self) -> str:
        return f"Validation abort because: {self.children}"

    

class AnyOf(Validator):
    '''
    限制值必须匹配任意一个验证器。
    允许的类型：Any
    '''
    allowTypes = None
    
    def __init__(self, *validators: Validator):
        self.validators = validators
    
    def _validate(self, value: Any, context: Any = None):
        errors = []
        
        for validator in self.validators:
            result = validator.validate(value, context)
            if result.success:
                return result
            else:
                errors.append(result.error)
        
        if len(errors) == 1:
            return ValidationResult(False, errors[0])
        else:
            return ValidationResult(False, AnyOfError(*errors))


class AllOf(Validator):
    '''
    限制值必须匹配所有指定验证器。

    允许的类型：Any
    '''
    allowTypes = None
    
    def __init__(self, *validators: Validator):
        self.validators = validators
    
    def _validate(self, value: Any, context: Any = None):
        errors = []

        for validator in self.validators:
            result = validator.validate(value, context)
            if not result.success:

                if isinstance(result.error, ValueTypeError):
                    return ValidationResult(False, AllOfAssertError(result.error))
                errors.append(result.error)
            
            
        if len(errors) == 0:
            return ValidationResult(True)
        elif len(errors) == 1:
            return ValidationResult(False, errors[0])
        else:
            return ValidationResult(False, AllOfError(*errors))

class Not(Validator):
    allowTypes = None
    
    def __init__(self, validator: Validator):
        self.validator = validator

    def _validate(self, value: Any, context: Any = None):
        result = self.validator.validate(value, context)
        if result.success:
            return ValidationResult(False, ValidationError("value must failed to validate."))
        else:
            return ValidationResult(True)