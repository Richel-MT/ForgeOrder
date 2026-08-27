from typing import Any

from .base import Validator, ValidationResult
from .typeOf import TypeOf
from .length import Length
from .choices import Choices

class StringOf(Validator):

    def __init__(self, minLength: int | None = None, maxLength: int | None = None, *choices):
        if choices and (minLength or maxLength):
            raise ValueError("choices and minLength/maxLength cannot be used together.")

        self.choices = choices
        self.minLength = minLength
        self.maxLength = maxLength

        self._validator = TypeOf(str)

        if minLength or maxLength:
            self._validator &= Length(minLength, maxLength)

        if choices:
            self._validator &= Choices(*choices)

    def _validate(self, value: Any, context: Any = None) -> ValidationResult:
        return self._validator.validate(value, context)
    