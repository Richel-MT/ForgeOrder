import sqlite3

from .exceptions import *

class Database:
    '''数据库连接类'''

    def __init__(self, db_name: str):
        self.db_name = db_name

        self.conn: sqlite3.Connection = None #type: ignore

    def connect(self):
        '''连接数据库'''

        try:
            self.conn = sqlite3.connect(self.db_name)

            self.conn.row_factory = sqlite3.Row

            self._init()
        except sqlite3.OperationalError as e:
            convert_error(e)

    def _init(self):
        '''开启外键约束与WAL模式'''
        self._is_available()

        self.execute("PRAGMA foreign_keys = ON;")
        self.execute("PRAGMA journal_mode = WAL;")
        self.commit()

    def _is_available(self):
        '''检查数据库连接是否有效'''
        if self.conn is None:
            raise NotConnectedError()

    def close(self):
        '''关闭数据库连接'''
        self._is_available()

        self.conn.close()
        self.conn = None #type: ignore

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor: #type: ignore
        '''执行SQL语句，返回游标对象'''
        self._is_available()

        try:
            cursor = self.conn.execute(sql, params)

            return cursor
        
        except sqlite3.Error as e:
            convert_error(e)

    def executescript(self, script: str):
        '''执行SQL脚本，返回游标对象'''
        self._is_available()

        try:
            cursor = self.conn.executescript(script)

            return cursor
        except sqlite3.Error as e:
            convert_error(e)

    def commit(self):
        '''提交事务'''
        self._is_available()

        self.conn.commit()

    def rollback(self):
        '''回滚事务'''
        self._is_available()

        self.conn.rollback()




if __name__ == "__main__":
    db = Database("forgeorder.db")
    db.connect()
    # db.test()
