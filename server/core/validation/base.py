from dataclasses import dataclass

from ._errors import ValidationError

@dataclass
class ValidationResult:
    success: bool
    error: 'ValidationError | None' = None
    # can_fix: bool = True

    def __bool__(self):
        return self.success

