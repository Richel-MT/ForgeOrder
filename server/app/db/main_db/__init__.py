import os

import extensions
from core.db.sql_parse import SqlParse
from core.db.database import Database
from .users import Users
from .tables import Tables
from .orders import Orders
from .dishes import DishesCategory, Dishes
from .settings import Settings
from .print_task import PrintTask

class MainDatabase(Database):
    def __init__(self, db_name: str) -> None:
        super().__init__(db_name)
        self.connect()

        self._init()

        self.users = Users(self.conn, self.sql_parse)
        
        self.tables = Tables(self.conn, self.sql_parse)

        self.orders = Orders(self.conn, self.sql_parse)

        self.category = DishesCategory(self.conn, self.sql_parse)

        self.dishes = Dishes(self, self.conn, self.sql_parse)

        self.settings = Settings(self.conn, self.sql_parse)

        self.print_task = PrintTask(self.conn, self.sql_parse)
        
    def _init(self):
        # 获取res
        res_path = os.path.join(extensions.root_dir, "res")

        sql_file = os.path.join(res_path, "main")

        # 执行sql_parse
        self.sql_parse = SqlParse(sql_file)


        # 执行初始化命令
        self.conn.executescript(self.sql_parse.get("main.init"))
        self.conn.commit()