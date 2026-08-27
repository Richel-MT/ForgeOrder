from dataclasses import dataclass
from typing import Any

from .validators import Validator
from .base import ValidationResult
from ._errors import ValueTypeError

@dataclass
class FieldDefinition:
    key: str
    valueType: type
    default: Any
    validator: 'Validator | None' = None

    def validate(self, value: Any):
        # print(type(value), self.value_type)
        if isinstance(value, self.valueType):
            if self.validator:
                return self.validator.validate(value)
            else:
                return ValidationResult(True)
        else:
            return ValidationResult(False, ValueTypeError(self.valueType))
        

  