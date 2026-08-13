from typing import TypedDict

from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class _Row(TypedDict):
    id: int
    key: str
    value: str

class SettingsRepository(Repository[_Row]):
    tableName = "settings"

    columns = [
        Column("id", Integer(), primary_key=True, autoIncrement=True),  # 主键
        Column("key", String(), notNull=True, unique=True),  # 键
        Column("value", String(), notNull=True),  # 值
    ]