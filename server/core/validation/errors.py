from dataclasses import dataclass
from typing import Any


class ValidationError:
    msg : str 

    def __init__(self, msg: str = ""):
        self.msg = msg

    def fix(self, property):
        '''
        返回修复好的值
        '''
        return property.default

    def __str__(self) -> str:
        return self.msg



@dataclass
class ValueTypeError(ValidationError):
    expectedType: type

    def __str__(self) -> str:
        return f"The handler only allows {self.expectedType} type."




class EmptyError(ValidationError):
    def __str__(self):
        return "The value cannot be empty."

@dataclass
class IntervalError(ValidationError):
    interval: Any

    def __str__(self):
        return f"Value must be in {self.interval}"

    

    
@dataclass
class LengthError(ValidationError):
    min: int | None = None
    max: int | None = None

    def __str__(self) -> str:
        return f"The length of value must be between {self.min} and {self.max}."


@dataclass
class ChoicesError(ValidationError):
    choices: tuple[Any, ...]

    def __str__(self) -> str:
        return f"The value must be in {self.choices}"




class AnyOfError(ValidationError):  
    children: list[ValidationError]

    def __init__(self, *children):
        self.children = list(children)

    def __str__(self) -> str:
        return "The value must match any of the following validators: " + ", ".join([str(child) for child in self.children])



class AllOfError(ValidationError):
    children: list[ValidationError]

    def __init__(self, *children):
        self.children = list(children)

    def __str__(self) -> str:
        return "The value must match all of the following validators: " + ", ".join([str(child) for child in self.children])


class ForEachError(ValidationError):
    children: list[ValidationError]

    def __init__(self, *children):
        self.children = list(children)

    def __str__(self) -> str:
        return "Each element of the value must match the following validators: " + ", ".join([str(child) for child in self.children])


class FieldTypeError(ValidationError):
    fieldKey: str
    expectedType: type

    def __init__(self, fieldKey: str, expectedType: type):
        self.fieldKey = fieldKey
        self.expectedType = expectedType

    def __str__(self) -> str:
        return f"Field '{self.fieldKey}' must be of type {self.expectedType}."

class MissingRequiredFieldError(ValidationError):
    fieldKey: str

    def __init__(self, fieldKey: str):
        self.fieldKey = fieldKey

    def __str__(self) -> str:
        return f"Missing required field '{self.fieldKey}'."

class FieldValidationError(ValidationError):
    fieldKey: str
    error: ValidationError

    def __init__(self, fieldKey: str, error: ValidationError):
        self.fieldKey = fieldKey
        self.error = error

    def __str__(self) -> str:
        return f"Field '{self.fieldKey}' validation error: {self.error}"

class UndefinedFieldError(ValidationError):
    fieldKey: str

    def __init__(self, fieldKey: str):
        self.fieldKey = fieldKey

    def __str__(self) -> str:
        return f"Field '{self.fieldKey}' is not defined in the schema."


class DictOfError(ValidationError):
    children: list[ValidationError]

    def __init__(self, *children):
        self.children = list(children)

    def __str__(self) -> str:
        return "Dictionary field validation failed:  " + ", ".join([str(child) for child in self.children])
