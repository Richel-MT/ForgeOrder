from typing import Any
from dataclasses import dataclass
from .base import Validator, ValidationResult

# 仅供内部使用！

@dataclass(init=False, eq=False)
class AlwaysPass(Validator):
    allowTypes = None
    def _validate(self, value: Any, context: Any = None) -> ValidationResult:
        return ValidationResult(True, None)