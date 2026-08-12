
from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class UsersRepository(Repository):

    table_name = "users"

    columns = [
        Column("id", Integer(), primary_key=True, auto_increment=True),  # 主键, auto increment
        Column("username", String(), not_null=True, unique=True),

        Column("password", String(), not_null=True),

        Column("is_admin", Boolean(), not_null=True, default=False),  # 是否管理员
        Column("is_available", Boolean(), not_null=True, default=True),  # 是否可用

        Column("created_at", DateTime(), not_null=True),  # 创建时间
        Column("last_login_at", DateTime()),  # 最后登录时间
    ]