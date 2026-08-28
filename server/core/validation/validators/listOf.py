from typing import Any

from .base import Validator, ValidationResult
from .typeOf import TypeOf
from .forEach import ForEach


class ListOf(Validator):
    allowTypes = None

    def __init__(self, *subValidators: Validator):

        self.subValidators: tuple[Validator, ...] = subValidators
        self._validator = TypeOf(list) & ForEach(*subValidators)

    def _validate(self, value: Any, context: Any = None) -> ValidationResult:
        return self._validator.validate(value, context)

    def mergeAnd(self, other: 'ListOf') -> 'ListOf':
        return ListOf(*(self.subValidators + other.subValidators))

    def __eq__(self, other):
        return isinstance(other, ListOf) and self.subValidators == other.subValidators
    


        