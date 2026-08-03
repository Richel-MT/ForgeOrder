
from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class TablesRepository(Repository):
    table_name = "tables"

    columns = [
        Column("id", Integer(), primary_key=True, auto_increment=True),  # 主键, auto increment
        Column("name", String(), not_null=True, unique=True),
        Column("is_available", Boolean(), not_null=True, default=True),  # 是否可用
        Column("is_deleted", Boolean(), not_null=True, default=False),  # 是否删除
    ]