from typing import Any, Literal
import warnings

from .base import Validator, ValidationResult
from .typeOf import TypeOf
from .length import Length
from .choices import Choices
from ..exceptions import NonMergeableValidatorError
from ..warnings import ValidationWarning

class StringOf(Validator):

    def __init__(self, *choices, min: int | None = None, max: int | None = None, ):
        if choices and (min or max):
            raise ValueError("choices and minLength/maxLength cannot be used together.")

        self.choices = choices
        self.minLength = min
        self.maxLength = max

        self._validator = TypeOf(str)
        self._length = None
        self._choices = None

        if min or max:
            self._length = Length(min, max)
            self._validator &= self._length


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

    def __repr__(self):
        args = []

        args.append(f"min={self.minLength}") if self.minLength is not None else ...
        args.append(f"max={self.maxLength}") if self.maxLength is not None else ...
        args.append(f"choices={self.choices}")     if self.choices else ""

        return f"StringOf({", ".join(args)})"

    