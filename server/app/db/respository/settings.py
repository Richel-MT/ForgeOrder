from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class SettingsRepository(Repository):
    table_name = "settings"

    columns = [
        Column("id", Integer(), primary_key=True, auto_increment=True),  # 主键
        Column("key", String(), not_null=True, unique=True),  # 键
        Column("value", String(), not_null=True),  # 值
    ]
