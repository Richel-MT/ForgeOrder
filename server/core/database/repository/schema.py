from dataclasses import dataclass
from typing import Literal, Any
import json
import datetime

from .exceptions import *
from core.typeConvert import converter, TypeConvertError

@dataclass
class ColumnType:
    '''列的类型'''
    origin_type: Literal["INTEGER", "REAL", "TEXT", "BLOB", "NULL"]
    py_type: type | tuple[type, ...]

    
    def validate_type(self, value: Any) -> Any:
        '''验证值是否符合类型要求'''
        if value is not None and not isinstance(value, self.py_type):
            # 类型不正确，尝试转换
            try:
                value_new = converter.convert(value, self.py_type)


                return value_new
            except TypeConvertError:
                # 无法转换，抛出异常
                raise TypeMismatchError(self.py_type, type(value)) #type: ignore
        else:
            return value

    def convert_to(self, value: Any) -> Any:
        '''将值转换为数据库可用的类型'''
        if value is None:
            return None
        
        return value

    def convert_from(self, value: Any) -> Any:
        '''将数据库可用的类型转换为原始类型'''

        if value is None:
            return None
        
        return value

@dataclass
class String(ColumnType):
    '''字符串类型，可指定长度'''
    origin_type = "TEXT"

    def __init__(self, length: int | None = None):
        self.origin_type = "TEXT"
        self.length = length

        super().__init__("TEXT", str)

    def convert_to(self, value: str) -> str:
        if value is None:
            return None
        
        if self.length is not None and len(value) > self.length:
            raise StringLengthError(self.length, value)

        return value

    def convert_from(self, value: str) -> str:
        if value is None:
                    return None
        return value

class Integer(ColumnType):
    '''整数类型'''
    origin_type = "INTEGER"
    def __init__(self):
        super().__init__("INTEGER", int)

class Real(ColumnType):
    '''浮点数类型'''
    origin_type = "REAL"

    def __init__(self):
        super().__init__("REAL", float)

class JSON(ColumnType):
    '''JSON类型'''
    origin_type = "TEXT"

    def __init__(self):
        super().__init__("TEXT", (dict, list))

    def convert_to(self, value: dict | list) -> str:
        if value is None:
                    return None
        
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception as e:
            raise InvalidJsonError(e)

    def convert_from(self, value: str) -> dict | list:
        if value is None:
                    return None

        try:
            return json.loads(value)
        except Exception as e:
            raise InvalidJsonError(e)

class DateTime(ColumnType):
    '''日期时间类型'''
    origin_type = "TEXT"

    def __init__(self):
        super().__init__("TEXT", datetime.datetime)

    def convert_to(self, value: datetime.datetime) -> str:
        if value is None:
                    return None
        
        return value.isoformat()

    def convert_from(self, value: str) -> datetime.datetime:
        if value is None:
                    return None
        
        return datetime.datetime.fromisoformat(value)

class Boolean(ColumnType):
    '''布尔类型'''
    origin_type = "INTEGER"

    def __init__(self):
        super().__init__("INTEGER", bool)

    def convert_to(self, value: bool) -> int:
        if value is None:
                    return None
        return int(value)
    
    def convert_from(self, value: int) -> bool:
        if value is None:
                    return None
        return bool(value)

    








