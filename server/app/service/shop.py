import datetime
from enum import Enum, auto
from typing import cast

from .base import Service, Result
from app.db.respository import RepositoryManager
from core.database.repository.exceptions import RecordNotFoundError

class ResultCode(Enum):
    SUCCESS = auto()

    CATEGORY_NOT_FOUND = auto()
    DISH_NOT_FOUND = auto()

class DishCategory:

    def __init__(self, repos: RepositoryManager, parent: 'ShopService'):
        self.repos = repos
        self.parent = parent

    def get_all(self):
        '''
        获取所有菜品的分类。
        '''
        result = self.repos.dishes_category.get_all(is_deleted=False)
        return Result(self.parent.RESULT.SUCCESS, result)

    def create(self, name: str):
        '''
        创建菜品分类。
        '''
        category_id = self.repos.dishes_category.insert(name=name)

        self.repos.dishes_category.commit()

        return Result(self.parent.RESULT.SUCCESS, category_id)

    def update(self, category_id: int, name: str):
        '''
        更新菜品分类的名称。
        '''
        try:
            self.repos.dishes_category.update(
                where={"id": category_id, "is_deleted": False},
                data={"name": name}
            )

            self.repos.dishes_category.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        return Result(self.parent.RESULT.SUCCESS)

    def delete(self, category_id: int):
        '''
        （软）删除菜品分类。
        '''
        name = datetime.datetime.now().strftime("deleted_at_%Y%m%d%H%M%S")

        try:
            self.repos.dishes_category.update(
                where={"id": category_id},
                data={"is_deleted": True, "name": name}
            )

            self.repos.dishes_category.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        

        return Result(self.parent.RESULT.SUCCESS, name)

    def get(self, category_id: int):
        '''
        获取一个菜品分类。
        '''

        category = self.repos.dishes_category.get(
                where={"id": category_id, "is_deleted": False}
            )

        if not category:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        return Result(self.parent.RESULT.SUCCESS, category["name"])

class Dishes:

    def __init__(self, repos: RepositoryManager, parent: 'ShopService'):
        self.repos = repos
        self.parent = parent

    def get_all_v1(self):
        '''
        获取所有菜品。兼容的旧版本API。
        '''

        # 准备返回值的结构
        result_categories = {}
        result_dishes = {}

        # 获取菜品分类、菜品、菜品统计信息、菜品选项
        category_rows = cast(list, self.parent.dishes_category.get_all().data)

        dish_rows = self.repos.dishes.get_all(is_deleted=False)
        dish_stats_rows = self.repos.dish_stats.get_all(is_deleted=False)
        dish_choices_rows = self.repos.dish_choices.get_all(is_deleted=False)

        # 处理返回值
        # 1、处理菜品分类信息，将其转换为{id:名称}的形式
        result_categories = {row["id"]: row["name"] for row in category_rows}

        # 2、初始化菜品结果的结构
        result_dishes = {row["name"]: [] for row in dish_rows}

        # 3、构建菜品统计信息和菜品选项信息的索引以快速访问
        dish_stats_index = {row["dish_id"]: row for row in dish_stats_rows}

        dish_choices_index = {}

        for choice in dish_choices_rows:
            dish_id = choice["dish_id"]

            if dish_id not in dish_choices_index:
                dish_choices_index[dish_id] = {}

            dish_choices_index[dish_id][choice["name"]] = choice["options"]
        

        # 3、遍历菜品，将菜品信息组装到结果中
        for dish in dish_rows:

            # 获取菜品的分类名称
            category_id = dish["category"]
            category_name = result_categories[category_id]

            # 将菜品的统计信息添加到菜品信息中
            dish_ = dish.copy()
            dish_["stats"] = dish_stats_index.get(dish_["id"], {})

            # 将菜品的选项信息添加到菜品信息中
            dish_["choices"] = dish_choices_index.get(dish_["id"], {})

            result_dishes[category_name].append(dish_)


        return Result(self.parent.RESULT.SUCCESS, (result_categories, result_dishes))


    def create(self,
            name: str,
            price: int,
            category_id: int,
            description: str = "",
            is_available: bool = True,
            choices: dict = {}
            ):

        '''
        创建菜品。
        '''

        # 验证分类是否存在
        if self.parent.dishes_category.get(category_id).code != self.parent.RESULT.SUCCESS:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)
        
        create_time = datetime.datetime.now()

        # 插入菜品
        dish_id = self.repos.dishes.insert(
            name=name,
            price=price,
            description=description,
            image="",
            category=category_id,
            is_available=is_available,
            created_at=create_time
        )

        self.repos.dishes.commit()

        return Result(self.parent.RESULT.SUCCESS, dish_id)


    def get(self, dish_id: int):
        '''获取菜品信息'''

        dish = self.repos.dishes.get(id=dish_id)

        if not dish:
            return Result(self.parent.RESULT.DISH_NOT_FOUND)
        
        dish_stats = self.repos.dish_stats.get(id=dish_id)
        dish_choices = self.repos.dish_choices.get_all(dish_id=dish_id, is_deleted=False)

        dish["stats"] = dish_stats
        dish["choices"] = dish_choices

        return Result(self.parent.RESULT.SUCCESS, dish)

    def delete(self, dish_id: int):
        '''
        （软）删除菜品。
        '''
        
        code, name = self.get(dish_id)

        if code != self.parent.RESULT.SUCCESS:
            return Result(code)

        
        try:
            self.repos.dishes.update(
                where={"id": dish_id},
                data={"is_deleted": True, "name": name}
            )

            self.repos.dishes.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.DISH_NOT_FOUND)

        return Result(self.parent.RESULT.SUCCESS, name)

    



class ShopService(Service):
    RESULT = ResultCode

    def __init__(self, repo_manager: RepositoryManager):
        super().__init__(repo_manager)

        self.dishes_category = DishCategory(repo_manager, self)
        self.dishes = Dishes(repo_manager, self)
        
