import sqlite3

from core.db.sql_parse import SqlParse

class Settings:
    def __init__(self, conn: sqlite3.Connection, sql_parse: SqlParse):
        self.conn = conn
        self.sql_parse = sql_parse

        self.conn.execute(self.sql_parse.get("settings.create"))
        self.conn.commit()
        

    def get(self, key: str):
        cursor = self.conn.execute(self.sql_parse.get("settings.get"), (key,))
        
        
        result = cursor.fetchone()

        if result:
            
            return dict(result)
        else:
            return None

    def update(self, key: str, value: str):
        cursor = self.conn.execute(self.sql_parse.get("settings.update"),
                              (key, value))
        self.conn.commit()

        return cursor.lastrowid

    def insert(self, key: str, value: str):
        self.conn.execute(self.sql_parse.get("settings.insert"),
                              (key, value, ))
        self.conn.commit()
