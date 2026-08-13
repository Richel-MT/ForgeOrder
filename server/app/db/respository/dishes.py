from typing import TypedDict
import datetime

from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class _DishesCategoryRow(TypedDict):
    id: int
    name: str
    isDeleted: bool

class DishesCategoryRepository(Repository[_DishesCategoryRow]):
    tableName = "dishesCategory"

    columns = [
        Column("id", Integer(), primary_key=True, autoIncrement=True),  # 主键
        Column("name", String(), notNull=True),  # 名称
        Column("isDeleted", Boolean(), notNull=True, default=False),  # 是否删除
    ]

class _DishesRow(TypedDict):
    id: int
    name: str
    price: int
    description: str | None
    image: str | None
    category: int
    isAvailable: bool
    createdAt: datetime.datetime
    isDeleted: bool

class DishesRepository(Repository[_DishesRow]):
    tableName = "dishes"

    columns = [
        Column("id", Integer(), primary_key=True, autoIncrement=True),  # 主键
        Column("name", String(), notNull=True),  # 名称
        Column("price", Integer(), notNull=True),  # 价格，单位：分
        Column("description", String()),  # 描述
        Column("image", String()),  # 图片
        Column("category", Integer(), notNull=True, foreign=("dishesCategory", "id")),  # 分类
        Column("isAvailable", Boolean(), notNull=True, default=True),  # 是否可用
        Column("createdAt", DateTime(), notNull=True),  # 创建时间
        Column("isDeleted", Boolean(), notNull=True, default=False),  # 是否删除
    ]

class _DishStatsRow(TypedDict):
    id: int
    totalSales: int
    monthlySales: int
    updatedAt: datetime.datetime

class DishStatsRepository(Repository[_DishStatsRow]):
    tableName = "dishStats"

    columns = [
        Column("id", Integer(), primary_key=True, foreign=("dishes", "id")),  # 主键
        
        Column("totalSales", Integer(), notNull=True, default=0),  # 总销售量
        Column("monthlySales", Integer(), notNull=True, default=0),  # 月销售量
        Column("updatedAt", DateTime(), notNull=True),  # 更新时间

    ]

class _DishChoicesRow(TypedDict):
    id: int
    dishId: int
    name: str
    options: dict

class DishChoicesRepository(Repository[_DishChoicesRow]):
    tableName = "dishChoices"

    columns = [
        Column("id", Integer(), primary_key=True, autoIncrement=True),  # 主键
        Column("dishId", Integer(), notNull=True, foreign=("dishes", "id")),  # 菜品ID

        Column("name", String(), notNull=True),  # 名称
        Column("options", JSON(), notNull=True),  # 选项

    ]