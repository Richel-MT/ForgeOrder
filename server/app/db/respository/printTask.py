from typing import TypedDict
import datetime

from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class _Row(TypedDict):
    id: str
    status: int
    content: dict
    context: dict
    errorMessage: str | None
    createdAt: datetime.datetime
    startedAt: datetime.datetime | None
    finishedAt: datetime.datetime | None

class PrintTaskRepository(Repository[_Row]):
    tableName = "printTask"

    columns = [
        Column("id", String(36), primaryKey=True, notNull=True),  # 主键, uuid v7
        Column("status", Integer(), notNull=True, default=0),  # 状态, 0：等待中 -- 1：打印中 -- 2：成功 --3：错误
        
        Column("content", JSON(), notNull=True),  # 打印内容
        Column("context", JSON(), notNull=True),  # 打印上下文

        Column("errorMessage", String()),  # 错误信息

        Column("createdAt", DateTime(), notNull=True),  # 创建时间
        Column("startedAt", DateTime()),  # 开始打印时间
        Column("finishedAt", DateTime()),  # 完成时间

    ]