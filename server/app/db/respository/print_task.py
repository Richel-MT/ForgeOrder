from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class PrintTaskRepository(Repository):
    table_name = "print_task"

    columns = [
        Column("id", String(36), primary_key=True, not_null=True),  # 主键, uuid v7
        Column("status", Integer(), not_null=True, default=0),  # 状态, 0：等待中 -- 1：打印中 -- 2：成功 --3：错误
        
        Column("content", JSON(), not_null=True),  # 打印内容
        Column("context", JSON(), not_null=True),  # 打印上下文

        Column("error_message", String()),  # 错误信息

        Column("created_at", DateTime(), not_null=True),  # 创建时间
        Column("started_at", DateTime()),  # 开始打印时间
        Column("finished_at", DateTime()),  # 完成时间

    ]  

