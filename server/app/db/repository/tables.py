
from typing import TypedDict

from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class _Row(TypedDict):
    id: int
    name: str
    isAvailable: bool
    isDeleted: bool

class TablesRepository(Repository[_Row]):
    tableName = "tables"

    columns = [
        Column("id", Integer(), primaryKey=True, autoIncrement=True),  # 主键, auto increment
        Column("name", String(), notNull=True, unique=True),
        Column("isAvailable", Boolean(), notNull=True, default=True),  # 是否可用
        Column("isDeleted", Boolean(), notNull=True, default=False),  # 是否删除
    ]