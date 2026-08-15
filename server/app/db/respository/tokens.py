from typing import TypedDict
import datetime

from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class _Row(TypedDict):
    id: int
    userId: int
    token: str
    status: int
    expireTime: datetime.datetime
    ip: str

class TokenRepository(Repository[_Row]):

    tableName = 'tokens'

    columns = [
        Column('id', Integer(), primaryKey=True, autoIncrement=True),
        Column('userId', Integer(), notNull=True, foreign=('users', 'id')),
        Column('token', String(), notNull=True),
        Column('status', Integer(), notNull=True, default=0), # 0:可用 1:已过期 2:已退出登录 3:旧设备
        Column('expireTime', DateTime(), notNull=True),
        Column('ip', String(), notNull=True),
    ]