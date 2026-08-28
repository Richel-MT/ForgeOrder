from typing import Any, Literal

from .base import Validator, ValidationResult
from .typeOf import TypeOf
from .length import Length
from .choices import Choices
from ..exceptions import NonMergeableValidatorError

class StringOf(Validator):

    def __init__(self, minLength: int | None = None, maxLength: int | None = None, *choices):
        if choices and (minLength or maxLength):
            raise ValueError("choices and minLength/maxLength cannot be used together.")

        self.choices = choices
        self.minLength = minLength
        self.maxLength = maxLength

        self._validator = TypeOf(str)
        self._length = None
        self._choices = None

        if minLength or maxLength:
            self._length = Length(minLength, maxLength)
            self._validator &= self._length

        if choices:
            self._choices = Choices(*choices)

            self._validator &= self._choices

    def _validate(self, value: Any, context: Any = None) -> ValidationResult:
        return self._validator.validate(value, context)

    def _merge(self, other: 'StringOf', mergeType: Literal["and", "or"]) -> 'StringOf':
        if self._length is not None:
            if other._length is not None:
                instance = StringOf()

                instance._length = self._length.mergeAnd(other._length) if mergeType == "and" else self._length.mergeOr(other._length)

                return instance
            else:
                raise NonMergeableValidatorError(type(self))

        elif self._choices is not None:
            if other._choices is not None:
                instance = StringOf()

                instance._choices = self._choices.mergeAnd(other._choices) if mergeType == "or" else self._choices.mergeOr(other._choices)

                return instance
            else:
                raise NonMergeableValidatorError(type(self))

        else:
            return other


    def mergeAnd(self, other: 'StringOf') -> 'StringOf':
        return self._merge(other, "and")

    def mergeOr(self, other: 'StringOf') -> 'StringOf':
        return self._merge(other, "or")

    def __eq__(self, other):
        return isinstance(other, StringOf) and self._validator == other._validator

    