from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class TokenRepository(Repository):

    table_name = 'tokens'

    columns = [
        Column('id', Integer(), primary_key=True, auto_increment=True),
        Column('user_id', Integer(), not_null=True, foreign=('users', 'id')),
        Column('token', String(), not_null=True),
        Column('status', Integer(), not_null=True, default=0), # 0:可用 1:已过期 2:已退出登录 3:旧设备
        Column('expire_time', DateTime(), not_null=True),
        Column('ip', String(), not_null=True),
    ]