from typing import Any

from .base import Validator
from ..base import ValidationResult
from ..errors import *
from ..condition import Condition
class AnyOf(Validator):
    '''
    限制值必须匹配任意一个验证器。
    允许的类型：Any
    '''
    allow_types = None
    
    def __init__(self, *validators: Validator):
        self.validators = validators
    
    def _validate(self, value: Any):
        errors = []
        
        for validator in self.validators:
            result = validator.validate(value)
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
    allow_types = None
    
    def __init__(self, *validators: Validator):
        self.validators = validators
    
    def _validate(self, value: Any):
        errors = []

        for validator in self.validators:
            result = validator.validate(value)
            if not result.success:
                errors.append(result.error)
            
        if len(errors) == 0:
            return ValidationResult(True)
        elif len(errors) == 1:
            return ValidationResult(False, errors[0])
        else:
            return ValidationResult(False, AllOfError(*errors))

class Not(Validator):
    allow_types = None
    
    def __init__(self, validator: Validator):
        self.validator = validator

    def _validate(self, value: Any):
        result = self.validator.validate(value)
        if result.success:
            return ValidationResult(False, ValidationError("value must failed to validate."))
        else:
            return ValidationResult(True)


class If(Validator):
    allow_types = None
    
    def __init__(self, condition: Condition, validator: Validator):
        self.condition = condition
        self.validator = validator
    
    def _validate(self, value: Any):
        if self.condition.(value):
            return self.validator.validate(value)
        else:
            return ValidationResult(True)