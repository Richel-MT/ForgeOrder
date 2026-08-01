from dataclasses import dataclass
from typing import Any

from ..database import Database
from .schema import ColumnType
from .exceptions import ColumnNotFoundError, EmptyQueryCriteriaError

@dataclass
class Column:
    name: str
    column_type:  ColumnType

    primary_key: bool = False
    not_null: bool = False
    unique: bool = False

    foreign: tuple[str, str] | None = None # 外键，格式为 (表名, 列名)

    default: Any | None = None

    def __str__(self):
        tags = []
        if self.primary_key:
            tags.append('PRIMARY KEY')

        if self.not_null:
            tags.append('NOT NULL')

        if self.unique:
            tags.append('UNIQUE')

        if self.default is not None:
            tags.append(f'DEFAULT {self.column_type.convert_to(self.default)}')

        if self.foreign is not None:
            tags.append(f'REFERENCES {self.foreign[0]} ({self.foreign[1]})')

        return f"{self.name} {self.column_type.origin_type} {' '.join(tags)}"

class Repository:
    '''数据库仓库类，表操作'''

    table_name: str
    columns : list[Column]

    columns_index: dict[str, Column]

    def __init__(self, db: Database):
        self.db = db


        self.columns_index = {c.name: c for c in self.columns}

    def _init(self):
        '''初始化表结构'''
        sql = f'''
CREATE TABLE IF NOT EXISTS {self.table_name} (
    {', '.join([str(c) for c in self.columns])}
)'''
        self.db.execute(sql)



    def _convert_to(self, **kwargs):
        '''将Python类型转换为数据库可用的类型'''

        result = {}
        for key, value in kwargs.items():

            column_type = self.columns_index.get(key, None)
            if column_type is None:
                raise ColumnNotFoundError(key)
            
            column_type.column_type.validate_type(value)
            result[key] = column_type.column_type.convert_to(value)
        
        return result

    def _convert_from(self, **kwargs):
        '''将数据库中记录的类型转换为Python类型'''
        result = {}

        for key, value in kwargs.items():
            column_type = self.columns_index.get(key, None)
            if column_type is None:
                raise ColumnNotFoundError(key)
            
            
            result[key] = column_type.column_type.convert_from(value)

        return result

    def get(self, **kwargs):
        '''根据条件查询一条记录，无条件抛出异常'''

        if len(kwargs) == 0:
            raise EmptyQueryCriteriaError()

        kwargs = self._convert_to(**kwargs)
        sql = f'''
SELECT * FROM {self.table_name}
WHERE {' AND '.join([f'{key} = ?' for key in kwargs.keys()])}
'''
        cursor = self.db.execute(sql, tuple(kwargs.values()))

        result = cursor.fetchone()

        if result is None:
            return None
        
        return self._convert_from(**result)

    def get_all(self, **kwargs):
        '''根据条件查询所有记录，若无条件则返回所有记录'''

        if len(kwargs) == 0:
            # 查询所有值
            sql = f'''
SELECT * FROM {self.table_name}
'''

            cursor = self.db.execute(sql)

        else:
            # 查询指定值

            kwargs = self._convert_to(**kwargs)

            sql = f'''
SELECT * FROM {self.table_name}
WHERE {' AND '.join([f'{key} = ?' for key in kwargs.keys()])}
'''
            cursor = self.db.execute(sql, tuple(kwargs.values()))

        result = cursor.fetchall()

        return [self._convert_from(**row) for row in result]

    def insert(self, **kwargs):
        '''插入一条记录'''
        kwargs = self._convert_to(**kwargs)

        sql = f'''
INSERT INTO {self.table_name} ({', '.join([c for c in kwargs.keys()])})
VALUES ({', '.join(['?'] * len(kwargs))})
'''

        cursor = self.db.execute(sql, tuple(kwargs.values()))


        return cursor.lastrowid


    def update(self, where: dict, data: dict):
        '''更新表中的记录'''
        where = self._convert_to(**where)
        data = self._convert_to(**data)

        sql = f'''
UPDATE {self.table_name}
SET {', '.join([f'{key} = ?' for key in data.keys()])}
WHERE {' AND '.join([f'{key} = ?' for key in where.keys()])}

'''
        self.db.execute(sql, tuple(data.values()) + tuple(where.values()))


    def delete(self, where: dict):
        '''根据where删除表中的值'''
        where = self._convert_to(**where)
        sql = f'''
DELETE FROM {self.table_name}
WHERE {' AND '.join([f'{key} = ?' for key in where.keys()])}
'''
        
        self.db.execute(sql, tuple(where.values()))


    def commit(self):
        '''提交事务'''
        self.db.commit()

    def rollback(self):
        '''回滚事务'''
        self.db.rollback()


    
if __name__ == '__main__':
    from .schema import *
    db = Database('test.db')
    db.connect()

    class TestRepo(Repository):
        table_name: str = 'fuck'
        columns = [
        Column('id', Integer(), primary_key=True),
        Column('name', String(255), not_null=True),
        Column('age', Integer()),
        Column('email', String(255)),
        Column('created_at', DateTime()),
        Column('is_active', Boolean()),
        Column('data', JSON()),
    ]
        
    repo = TestRepo(db)
    repo._init()

    # repo.insert(name='test123', age=18, email='test@example.com')

    repo.update(where={
        "id": 1
    }, data={
        "age": 20,
    })

    print(repo.get(id=1))

    print(repo.get_all())


    repo.commit()
    
    
        