from typing import Any
from dataclasses import dataclass

from .base import Validator, ValidationResult
from .._errors import ValidationError

@dataclass
class ChoicesError(ValidationError):
    choices: tuple[Any, ...]

    def __str__(self) -> str:
        return f"The value must be in {self.choices}"


class Choices(Validator):
    '''
    限制值只能是指定的选项。
    允许的类型：Any
    '''
    allowTypes = None

    def __init__(self, *choices):
        self.choices = choices
        
    def _validate(self, value: Any, context: Any = None):
        if value in self.choices:
            return ValidationResult(True)
        else:
            return ValidationResult(False, ChoicesError(self.choices))

    def mergeOr(self, other: 'Choices'):
        return Choices(*(list(self.choices) + list(other.choices)))


    def __repr__(self):
        return f"Choices({", ".join([repr(choice) for choice in self.choices])})"

    def __eq__(self, other): return isinstance(other, Choices) and self.choices == other.choices
    