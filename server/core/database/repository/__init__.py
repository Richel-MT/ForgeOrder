from dataclasses import dataclass
from typing import Any, TypedDict, TypeVar, Generic, cast

from ..database import Database
from .schema import ColumnType
from .exceptions import ColumnNotFoundError, EmptyQueryCriteriaError, RecordNotFoundError


RowType = TypeVar('RowType', bound=TypedDict)


@dataclass
class Column:
    name: str
    columnType:  ColumnType

    primary_key: bool = False
    notNull: bool = False
    unique: bool = False

    autoIncrement: bool = False

    foreign: tuple[str, str] | None = None # 外键，格式为 (表名, 列名)

    default: Any | None = None

    def __str__(self):
        tags = []
        if self.primary_key:
            tags.append('PRIMARY KEY')

        if self.notNull:
            tags.append('NOT NULL')

        if self.unique:
            tags.append('UNIQUE')

        if self.default is not None:
            tags.append(f'DEFAULT {self.columnType.convertTo(self.default)}')

        if self.foreign is not None:
            tags.append(f'REFERENCES {self.foreign[0]} ({self.foreign[1]})')

        if self.autoIncrement:
            tags.append('AUTOINCREMENT')
            
        return f"{self.name} {self.columnType.originType} {' '.join(tags)}"

class Repository(Generic[RowType]):
    '''数据库仓库类，表操作'''

    tableName: str
    columns : list[Column]

    columnsIndex: dict[str, Column]

    Row: type[RowType]


    def __init__(self, db: Database):
        self.db = db


        self.columnsIndex = {c.name: c for c in self.columns}

        

    def _init(self):
        '''初始化表结构'''
        sql = f'''
CREATE TABLE IF NOT EXISTS {self.tableName} (
    {', '.join([str(c) for c in self.columns])}
)'''
        self.db.execute(sql)



    def _convertTo(self, **kwargs):
        '''将Python类型转换为数据库可用的类型'''

        result = {}
        for key, value in kwargs.items():

            columnType = self.columnsIndex.get(key, None)
            if columnType is None:
                raise ColumnNotFoundError(key)
            
            value = columnType.columnType.validateType(value)

            result[key] = columnType.columnType.convertTo(value)
        
        return result

    def _convertFrom(self, **kwargs):
        '''将数据库中记录的类型转换为Python类型'''
        result = {}

        for key, value in kwargs.items():
            columnType = self.columnsIndex.get(key, None)
            if columnType is None:
                raise ColumnNotFoundError(key)
            
            
            result[key] = columnType.columnType.convertFrom(value)

        return result

    def get(self, **kwargs) -> 'RowType | None':
        '''根据条件查询一条记录，无条件抛出异常'''

        if len(kwargs) == 0:
            raise EmptyQueryCriteriaError()

        kwargs = self._convertTo(**kwargs)
        sql = f'''
SELECT * FROM {self.tableName}
WHERE {' AND '.join([f'{key} = ?' for key in kwargs.keys()])}
'''
        cursor = self.db.execute(sql, tuple(kwargs.values()))

        result = cursor.fetchone()

        if result is None:
            return None
        
        return cast(RowType, self._convertFrom(**result))

    def getAll(self, **kwargs) -> 'list[RowType]':
        '''根据条件查询所有记录，若无条件则返回所有记录'''

        if len(kwargs) == 0:
            # 查询所有值
            sql = f'''
SELECT * FROM {self.tableName}
'''

            cursor = self.db.execute(sql)

        else:
            # 查询指定值

            kwargs = self._convertTo(**kwargs)

            sql = f'''
SELECT * FROM {self.tableName}
WHERE {' AND '.join([f'{key} = ?' for key in kwargs.keys()])}
'''
            cursor = self.db.execute(sql, tuple(kwargs.values()))

        result = cursor.fetchall()

        return cast(list[RowType], [self._convertFrom(**row) for row in result])

    def insert(self, **kwargs):
        '''插入一条记录'''
        kwargs = self._convertTo(**kwargs)

        sql = f'''
INSERT INTO {self.tableName} ({', '.join([c for c in kwargs.keys()])})
VALUES ({', '.join(['?'] * len(kwargs))})
'''

        cursor = self.db.execute(sql, tuple(kwargs.values()))


        return cursor.lastrowid


    def update(self, where: dict, data: dict):
        '''更新表中的记录'''
        where = self._convertTo(**where)
        data = self._convertTo(**data)

        sql = f'''
UPDATE {self.tableName}
SET {', '.join([f'{key} = ?' for key in data.keys()])}
WHERE {' AND '.join([f'{key} = ?' for key in where.keys()])}

'''
        cursor = self.db.execute(sql, tuple(data.values()) + tuple(where.values()))

        if cursor.rowcount == 0:
            raise RecordNotFoundError(where)

    def delete(self, where: dict):
        '''根据where删除表中的值'''
        where = self._convertTo(**where)
        sql = f'''
DELETE FROM {self.tableName}
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
        Column('name', String(255), notNull=True),
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


    repo.commit()
    
    
        