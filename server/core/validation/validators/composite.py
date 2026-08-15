from typing import Any

from .base import Validator
from ..base import ValidationResult
from ..errors import *
from ..condition import Condition
from ..exceptions import NotIterableError


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

class ForEach(Validator):
    '''
    对可迭代对象的每个元素进行验证
    允许的类型：任意可迭代对象
    '''
    allowTypes = None
    
    def __init__(self, validator: Validator):
        self.validator = validator

    def _validate(self, value: Any, context: Any = None):
        if not hasattr(value, "__iter__"):
            raise NotIterableError(ForEach, type(value))


        errors = []
        for index, item in enumerate(value):
            result = self.validator.validate(item, context)

            if not result.success:
                errors.append(result.error)

        if len(errors) == 0:
            return ValidationResult(True)
        else:
            return ValidationResult(False, ForEachError(*errors))

@dataclass
class _Field:
    key: str
    valueType: type
    required: bool
    validator: Validator | None = None

class DictOf(Validator):
    '''
    规定字典的键值对信息。键值对名称、类型、必填项、默认值、验证器。

    非严格模式下，未被定义的键值对将被忽略

    允许的类型：dict
    '''
    allowTypes = dict

    def __init__(self, *fields: _Field, strictMode: bool = False):
        self.fields: list[_Field] = list(fields)

        self.strictMode = strictMode

    
    def Field(self, key: str, valueType: type, required: bool, validator: Validator | None = None):
        field = _Field(key, valueType, required, validator)

        self.fields.append(field)
        return self

    def _validate(self, value: dict, context: Any = None):

        errors = []

        fieldKeys = []

        for field in self.fields:
            key = field.key

            fieldKeys.append(key)

            if key not in value:
                if field.required:
                    errors.append(MissingRequiredFieldError(key))
                    continue

            else:
                if not isinstance(value[key], field.valueType):
                    errors.append(FieldTypeError(key, field.valueType))
                    continue

                if field.validator is not None:
                    result = field.validator.validate(value[key], context)

                    if not result.success:
                        errors.append(FieldValidationError(key, result.error)) #type: ignore

        if self.strictMode:
            for key in value.keys():
                if key not in fieldKeys:
                    errors.append(UndefinedFieldError(key))
            

        if len(errors) == 0:
            return ValidationResult(True)
        else:
            return ValidationResult(False, DictOfError(*errors))

    
        
        


class If(Validator):
    allowTypes = None
    
    def __init__(self, condition: Condition, validator: Validator):
        self.condition = condition
        self.validator = validator

        self.elseValidator = None
    
    def _validate(self, value: Any, context: Any = None):
        if self.condition.check(context):
            return self._formatResult(self.validator.validate(value, context))
        elif self.elseValidator is not None:
            return self._formatResult(self.elseValidator.validate(value, context))
        else:
            return ValidationResult(True)

    def _formatResult(self, result: ValidationResult):
        if result.success:
            return result
        else:
            return ValidationResult(False, ValidationError(f"When the condition: '{self.condition}' pass, {result.error}"))

    def Elif(self, condition: Condition, validator: Validator):
        self.elseValidator = Elif(condition, validator)

        return self.elseValidator
    def Else(self, validator: Validator):
        self.elseValidator = Else(validator)
        return self.elseValidator
    
class Elif(If):
    pass

class Else(Validator):
    allowTypes = None

    def __init__(self, validator: Validator):
        self.validator = validator

    def _validate(self, value: Any, context: Any = None):
        return self.validator.validate(value, context)
