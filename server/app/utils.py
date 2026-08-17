from typing import TypedDict, cast

from flask import g as g_

from .log import RequestLogContext
from .routes.responseGenerator import ResponseGenerator
from core.database.database import Database
from app.db.repository import RepositoryManager

class UserInfo(TypedDict):
    id: int
    isAdmin: bool
    username: str

class GProxy:
    '''拥有类型提示的g对象'''

    requestId: str

    logger: RequestLogContext

    startTime: float

    res: ResponseGenerator

    args: dict

    userInfo: UserInfo

    database: Database

    repos: RepositoryManager

g = cast(GProxy, g_)
