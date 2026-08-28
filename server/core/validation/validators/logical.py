from typing import Any, cast
from dataclasses import dataclass
from collections import defaultdict, Counter
from functools import reduce

from .base import Validator, ValidationResult
from .._errors import ValidationError, ValueTypeError
from ..exceptions import NonMergeableValidatorError


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


def mergeValidator(parentValidatorClass: type[AnyOf] | type[AllOf], subValidators: list[Validator]):
    if len(subValidators) <= 1:
        return subValidators


    subValidators_ = []
    groups: dict[type[Validator], list[Validator]] = defaultdict(list)
    mergedValidators: list[Validator] = []

    # 展平
    for v in subValidators:

        if type(v) is parentValidatorClass:
            subValidators_.extend(v.validators)
        else:
            subValidators_.append(v)

    # 分类
    for v in subValidators_:
        groups[type(v)].append(v)

    # 合并
    for _, validators in groups.items():
        try:
            mergedValidators.append(reduce(
                (lambda x, y: (x.mergeAnd(y) if parentValidatorClass is AllOf else x.mergeOr(y)) if x != y else x),
                validators))
        except NonMergeableValidatorError:
            mergedValidators.extend(validators)

    return mergedValidators


  
class AnyOf(Validator):
    '''
    限制值必须匹配任意一个验证器。
    允许的类型：Any
    '''
    allowTypes = None

    def __new__(cls, *validators: Validator):
        mergedValidators = mergeValidator(cls, list(validators))

        if len(mergedValidators) == 1:
            return mergedValidators[0]
        else:
            instance =  super().__new__(cls, *mergedValidators)

            instance.validators = mergedValidators

            return instance

    
    def __init__(self, *validators: Validator):
        if not hasattr(self, 'validators'):
            self.validators = list(validators)

    def __repr__(self):
        return f"AnyOf({', '.join([repr(v) for v in self.validators])})"

    def __eq__(self, other):
        return isinstance(other, AnyOf) and Counter(self.validators) == Counter(other.validators)
    
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

    def __new__(cls, *validators: Validator):

        mergedValidator = mergeValidator(cls, list(validators))

        if len(mergedValidator) == 1:
            return mergedValidator[0]
        else:
            instance = super().__new__(cls,)

            instance.validators = mergedValidator

            return instance


    
    def __init__(self, *validators: Validator):
        if not hasattr(self, 'validators'):
            self.validators = list(validators)
    
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


    def __repr__(self):
        return f"AllOf({', '.join([repr(v) for v in self.validators])})"

    def __eq__(self, other):
        return isinstance(other, AllOf) and Counter(self.validators) == Counter(other.validators)

class Not(Validator):
    allowTypes = None

    def __new__(cls, validator: Validator):
        if isinstance(validator, Not):
            return validator.validator
        else:
            return super().__new__(cls)

    def __init__(self, validator: Validator):
        self.validator = validator

    def _validate(self, value: Any, context: Any = None):
        result = self.validator.validate(value, context)
        if result.success:
            return ValidationResult(False, ValidationError("value must failed to validate."))
        else:
            return ValidationResult(True)

    def __repr__(self):
        return f"Not({repr(self.validator)})"

    def __eq__(self, other):
        return isinstance(other, Not) and self.validator == other.validator
        