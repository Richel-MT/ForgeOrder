from typing import TypedDict
import datetime

from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class _Row(TypedDict):
        id: int
        username: str
        password: str
        isAdmin: bool
        isAvailable: bool
        createdAt: datetime.datetime
        lastLoginAt: datetime.datetime | None

class UsersRepository(Repository[_Row]):

    tableName = "users"


    columns = [
        Column("id", Integer(), primaryKey=True, autoIncrement=True),  # 主键, auto increment
        Column("username", String(), notNull=True, unique=True),

        Column("password", String(), notNull=True),

        Column("isAdmin", Boolean(), notNull=True, default=False),  # 是否管理员
        Column("isAvailable", Boolean(), notNull=True, default=True),  # 是否可用

        Column("createdAt", DateTime(), notNull=True),  # 创建时间
        Column("lastLoginAt", DateTime()),  # 最后登录时间
    ]


    
