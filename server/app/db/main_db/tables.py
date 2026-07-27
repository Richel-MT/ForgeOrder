import datetime
import sqlite3

from core.db.exceptions import NotFoundError
from core.db.sql_parse import SqlParse

class Tables:
    def __init__(self, conn: sqlite3.Connection, sql_parse: SqlParse):
        self.conn = conn
        self.sql_parse = sql_parse

        self.conn.execute(self.sql_parse.get("tables.create"))
        self.conn.commit()
        
        
    def new(self, name: str, is_available: bool = True):
        '''
        创建一个新桌。返回新桌的id。
        
        注意：若已存在相同桌名的桌，则会抛出ValueError，不抛出异常的方法为new_s。
        '''
        try:
            # 执行new命令以在tables表中创建新表
            cursor = self.conn.execute(
                self.sql_parse.get("tables.new"),
                (name, is_available)
                )
            
            self.conn.commit()

            return cursor.lastrowid
        
        except sqlite3.IntegrityError:
            raise ValueError(f"Table name {name} already exists")
    
    def new_s(self, name: str, is_available: bool = True):
        '''
        创建一个新桌。返回新桌的id。本方法的效果与new方法相同，只是在创建桌时不会抛出异常。

        注意：若已存在相同桌名的桌，则会返回None。
        '''
        cursor = self.conn.execute(
            self.sql_parse.get("tables.get_from_name"),
            (name,)
            )
        table = cursor.fetchone()
        if table:
            return None
        
        return self.new(name, is_available)
    
    def get_from_name(self, name: str):
        '''
        根据桌名获取桌信息。桌不存在将返回None。

        注意：数据库使用了Row factory，返回的桌信息为Row对象。
        '''
        cursor = self.conn.execute(
            self.sql_parse.get("tables.get_from_name"),
            (name,)
            )
        table = cursor.fetchone()
        if table:
            return table
        return None


    def get_all(self):
        '''
        获取所有餐桌。

        返回字典
        '''
        cursor = self.conn.execute(
            self.sql_parse.get("tables.get_all")
            )

        tables = cursor.fetchall()

        return [dict(table) for table in tables]

    def update(self, table_id: int, name: str, is_available: bool = True):
        '''
        更新桌信息。
        '''

        if self.get_from_name(name):
            raise ValueError(f"Table name {name} already exists")

        cursor = self.conn.execute(
            self.sql_parse.get("tables.update"),
            (name, is_available, table_id)
            )
        
        self.conn.commit()

        if cursor.rowcount == 0:
            raise NotFoundError(str(table_id))


    def soft_delete(self, table_id: int):
        '''
        软删除桌。
        '''
        cursor = self.conn.execute(
            self.sql_parse.get("tables.soft_delete"),
            (table_id,)
            )

        if cursor.rowcount ==  0:
            raise NotFoundError(str(table_id))

        self.conn.commit()

