from typing import TypedDict
from dataclasses import dataclass

from .field import RequestField
from .res_generator import ResponseInfo


class RoutesInfo(TypedDict):
    is_admin: bool
    auth: bool
    args: dict[str, RequestField]
    responses: list[ResponseInfo]








