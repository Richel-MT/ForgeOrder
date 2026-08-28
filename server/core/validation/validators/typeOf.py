from typing import Any

from .base import Validator, ValidationResult
from ..errors import ValueTypeError
class TypeOf(Validator):
    allowTypes = None

    def __init__(self, *valueTypes: type):
        self.valueTypes = valueTypes

    def _validate(self, value: Any, context: Any = None):
        if isinstance(value, self.valueTypes):
            return ValidationResult(True)
        else:
            return ValidationResult(False, ValueTypeError(self.valueTypes))

    def mergeOr(self, other: 'TypeOf') -> 'TypeOf':

        newTypes = set(self.valueTypes)

        newTypes.update(other.valueTypes)

        return TypeOf(*newTypes)

    def __repr__(self):
        return f"TypeOf({', '.join([valueType.__name__ for valueType in self.valueTypes])})"

    def __eq__(self, other):
        return isinstance(other, TypeOf) and self.valueTypes == other.valueTypes
        