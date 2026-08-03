from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class DishesCategoryRepository(Repository):
    table_name = "dishes_category"

    columns = [
        Column("id", Integer(), primary_key=True, auto_increment=True),  # 主键
        Column("name", String(), not_null=True),  # 名称
        Column("is_deleted", Boolean(), not_null=True, default=False),  # 是否删除
    ]

class DishesRepository(Repository):
    table_name = "dishes"

    columns = [
        Column("id", Integer(), primary_key=True, auto_increment=True),  # 主键
        Column("name", String(), not_null=True),  # 名称
        Column("price", Integer(), not_null=True),  # 价格，单位：分
        Column("description", String()),  # 描述
        Column("image", String()),  # 图片
        Column("category", Integer(), not_null=True, foreign=("dishes_category", "id")),  # 分类
        Column("is_available", Boolean(), not_null=True, default=True),  # 是否可用
        Column("created_at", DateTime(), not_null=True),  # 创建时间
        Column("is_deleted", Boolean(), not_null=True, default=False),  # 是否删除
    ]

class DishStatsRepository(Repository):
    table_name = "dish_stats"

    columns = [
        Column("id", Integer(), primary_key=True, foreign=("dishes", "id")),  # 主键
        
        Column("total_sales", Integer(), not_null=True, default=0),  # 总销售量
        Column("monthly_sales", Integer(), not_null=True, default=0),  # 月销售量
        Column("updated_at", DateTime(), not_null=True),  # 更新时间

    ]

class DishChoicesRepository(Repository):
    table_name = "dish_choices"

    columns = [
        Column("id", Integer(), primary_key=True, auto_increment=True),  # 主键
        Column("dish_id", Integer(), not_null=True, foreign=("dishes", "id")),  # 菜品ID

        Column("name", String(), not_null=True),  # 名称
        Column("options", JSON(), not_null=True),  # 选项
    ]