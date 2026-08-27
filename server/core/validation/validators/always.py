from typing import Any

from .base import Validator, ValidationResult

# 仅供内部使用！

class AlwaysPass(Validator):
    allowTypes = None
    def _validate(self, value: Any, context: Any = None) -> ValidationResult:
        return ValidationResult(True, None)