import traceback
from typing import Literal
import os

# import extensions

# def create_server_info_by_exception(e: Exception):
#     info = ""
#     for line in traceback.format_exception(type(e), e, e.__traceback__):
#         info += line
#         info += "\n"
    
#     return info

def padString(string: str,
               length: int,
               padChar: str = "0",
               position: Literal["left", "right"] = "left") -> str:
    '''
    根据长度补齐字符串
    '''

    if len(string) >= length:
        return string
    
    padLength = length - len(string)

    if position == "left":
        return padChar * padLength + string
    else:
        return string + padChar * padLength
    