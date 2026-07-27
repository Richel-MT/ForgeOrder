import sqlite3
import datetime

from core.db.sql_parse import SqlParse
from core.db.exceptions import NotFoundError


class PrintTask:
    def __init__(self, conn: sqlite3.Connection, sql_parse: SqlParse):
        self.conn = conn
        self.sql_parse = sql_parse

        self.conn.execute(self.sql_parse.get("print_task.create"))
        self.conn.commit()

    def new(self,
            id: str,
            content: str,
            created_at: datetime.datetime,
            context: str = "",
            ):
        
        self.conn.execute(self.sql_parse.get("print_task.new"),
                              (id, content, context, created_at))
        self.conn.commit()

        return id

    def get(self, id: str):
        cursor = self.conn.execute(self.sql_parse.get("print_task.get"),
                                   (id,))

        if cursor.rowcount == 0:
            raise NotFoundError(str(id))
        
        return dict(cursor.fetchone())

    def update(self,
            id: str,
            status: int,
            error_message: str = None,
            started_at: datetime.datetime = None,
            finished_at: datetime.datetime = None):

        cursor = self.conn.execute(self.sql_parse.get("print_task.update"),
                                  (status, error_message, started_at, finished_at, id))
        
        self.conn.commit()

        if cursor.rowcount == 0:
            raise NotFoundError(str(id))
     