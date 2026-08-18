from dataclasses import dataclass
from typing import Any

from core.validation.field import FieldDefinition
from core.validation.validators import *

@dataclass
class RequestParameterField(FieldDefinition):
    pass

@dataclass
class BodyField(RequestParameterField):    
    '''请求头中的参数验证'''
    def __init__(self,
                key: str,
                valueType: type,
                required: bool,
                default: Any = None,
                validator: Validator | None = None
                ):
        super().__init__(key, valueType, default, validator)

        self.required : bool = required

        if not required and default is None:
            raise ValueError(f"unrequired field {key} must have a default value.")

@dataclass
class PathField(RequestParameterField):
    '''URL路径中的参数验证'''
    def __init__(self,
                 key: str,
                 valueType: type,
                 validator: Validator | None = None
                 ):
        super().__init__(key, valueType, None, validator)