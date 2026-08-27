from typing import Any
from dataclasses import dataclass

from .base import Validator, ValidationResult
from ..errors import ValidationError

class NotIterableError(Exception):
    '''
    传入的值不是可迭代对象
    '''
    def __init__(self, validatorClass: type, valueType: type):
        self.validatorClass = validatorClass
        self.valueType = valueType

        super().__init__(
            f"Validator ' {self.validatorClass.__name__}' requires an iterable value, but got {self.valueType}."
        )


class ForEachError(ValidationError):
    children: list[ValidationError]

    def __init__(self, *children):
        self.children = list(children)

    def __str__(self) -> str:
        return "Each element of the value must match the following validators: " + ", ".join([str(child) for child in self.children])



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

