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
    allow_types = None
    
    def __init__(self, *validators: Validator):
        self.validators = validators
    
    def _validate(self, value: Any, context: Any = None):
        errors = []

        for validator in self.validators:
            result = validator.validate(value, context)
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

    def _validate(self, value: Any, context: Any = None):
        result = self.validator.validate(value, context)
        if result.success:
            return ValidationResult(False, ValidationError("value must failed to validate."))
        else:
            return ValidationResult(True)


class If(Validator):
    allow_types = None
    
    def __init__(self, condition: Condition, validator: Validator):
        self.condition = condition
        self.validator = validator

        self.else_validator = None
    
    def _validate(self, value: Any, context: Any = None):
        if self.condition.check(context):
            return self._format_result(self.validator.validate(value, context))
        elif self.else_validator is not None:
            return self._format_result(self.else_validator.validate(value, context))
        else:
            return ValidationResult(True)

    def _format_result(self, result: ValidationResult):
        if result.success:
            return result
        else:
            return ValidationResult(False, ValidationError(f"When the condition: '{self.condition}' pass, {result.error}"))

    def Elif(self, condition: Condition, validator: Validator):
        self.else_validator = Elif(condition, validator)

        return self.else_validator
    def Else(self, validator: Validator):
        self.else_validator = Else(validator)
        return self.else_validator
    
class Elif(If):
    pass

class Else(Validator):
    allow_types = None

    def __init__(self, validator: Validator):
        self.validator = validator

    def _validate(self, value: Any, context: Any = None):
        return self.validator.validate(value, context)
