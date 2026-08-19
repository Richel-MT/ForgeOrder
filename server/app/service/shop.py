import datetime
from enum import Enum, auto
from typing import cast

from .base import Service, Result
from app.db.repository import RepositoryManager
from core.database.repository.exceptions import RecordNotFoundError, TypeMismatchError
from core.database.database.exceptions import UniqueConstraintError

class ResultCode(Enum):
    SUCCESS = auto()

    CATEGORY_NOT_FOUND = auto()
    DISH_NOT_FOUND = auto()


    CHANGED_ITEMS_NOT_FOUND = auto() # 更改的信息不存在

    VALUE_ERROR = auto() # 更改的信息 值非法

    CHOICE_NOT_FOUND = auto()

    CATEGORY_ALREADY_EXIST = auto()


    TABLE_ALREADY_EXIST = auto()
    TABLE_NOT_FOUND = auto()


class DishCategory:

    def __init__(self, repos: RepositoryManager, parent: 'ShopService'):
        self.repos = repos
        self.parent = parent

    def getAll(self):
        '''
        获取所有菜品的分类。
        '''
        result = self.repos.dishesCategory.getAll(isDeleted=False)
        return Result(self.parent.RESULT.SUCCESS, result)

    def create(self, name: str):
        '''
        创建菜品分类。
        '''
        try:
            categoryId = self.repos.dishesCategory.insert(name=name)
        except UniqueConstraintError:
            return Result(self.parent.RESULT.CATEGORY_ALREADY_EXIST)

        self.repos.dishesCategory.commit()

        return Result(self.parent.RESULT.SUCCESS, categoryId)

    def update(self, categoryId: int, name: str):
        '''
        更新菜品分类的名称。
        '''
        try:
            self.repos.dishesCategory.update(
                where={"id": categoryId, "isDeleted": False},
                data={"name": name}
            )

            self.repos.dishesCategory.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        return Result(self.parent.RESULT.SUCCESS)

    def delete(self, categoryId: int):
        '''
        （软）删除菜品分类。
        '''
        name = datetime.datetime.now().strftime("deleted_at_%Y%m%d%H%M%S")

        try:
            self.repos.dishesCategory.update(
                where={"id": categoryId},
                data={"isDeleted": True, "name": name}
            )

            self.repos.dishesCategory.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        

        return Result(self.parent.RESULT.SUCCESS, name)

    def get(self, categoryId: int):
        '''
        获取一个菜品分类。
        '''

        category = self.repos.dishesCategory.get(
                id=categoryId, isDeleted=False
            )

        if not category:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        return Result(self.parent.RESULT.SUCCESS, category["name"])

class Dishes:

    def __init__(self, repos: RepositoryManager, parent: 'ShopService'):
        self.repos = repos
        self.parent = parent

    def getAll(self):
        '''
        获取所有菜品。兼容的旧版本API。
        '''

        # 准备返回值的结构
        resultCategories = {}
        resultDishes = {}

        # 获取菜品分类、菜品、菜品统计信息、菜品选项
        categoryRows = cast(list, self.parent.dishesCategory.getAll().data)

        dishRows = self.repos.dishes.getAll(isDeleted=False)
        dishStatsRows = self.repos.dishStats.getAll()
        dishChoicesRows = self.repos.dishChoices.getAll()

        # 处理返回值
        # 1、处理菜品分类信息，将其转换为{id:名称}的形式
        resultCategories = {row["id"]: row["name"] for row in categoryRows}

        # 2、初始化菜品结果的结构
        resultDishes = {row["name"]: [] for row in categoryRows}

        # 3、构建菜品统计信息和菜品选项信息的索引以快速访问
        dishStatsIndex = {row["id"]: row for row in dishStatsRows}

        dishChoicesIndex = {}

        for choice in dishChoicesRows:
            dishId = choice["dishId"]

            if dishId not in dishChoicesIndex:
                dishChoicesIndex[dishId] = {}

            dishChoicesIndex[dishId][choice["name"]] = choice["options"]
        

        # 3、遍历菜品，将菜品信息组装到结果中
        for dish in dishRows:

            # 获取菜品的分类名称
            categoryId = dish["category"]
            categoryName = resultCategories[categoryId]

            # 将菜品的统计信息添加到菜品信息中
            dish_ = dict(dish.copy())
            
            dish_["stats"] = dishStatsIndex.get(dish_['id'], {})

            # 将菜品的选项信息添加到菜品信息中
            dish_["choices"] = dishChoicesIndex.get(dish_["id"], {})

            resultDishes[categoryName].append(dish_)


        return Result(self.parent.RESULT.SUCCESS, (resultCategories, resultDishes))


    def create(self,
            name: str,
            price: int,
            categoryId: int,
            description: str = "",
            isAvailable: bool = True,
            choices: dict[str, list] = {}
            ):

        '''
        创建菜品。
        '''

        # 验证分类是否存在
        if self.parent.dishesCategory.get(categoryId).code != self.parent.RESULT.SUCCESS:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)
        
        createTime = datetime.datetime.now()

        # 插入菜品
        dishId = self.repos.dishes.insert(
            name=name,
            price=price,
            description=description,
            image="",
            category=categoryId,
            isAvailable=isAvailable,
            createdAt=createTime
        )

        # 创建菜品统计信息
        self.repos.dishStats.insert(
            id=dishId,
            updatedAt=createTime
        )

        # 插入菜品选项信息
        for choiceName, options in choices.items():
            self.repos.dishChoices.insert(
                dishId=dishId,
                options=options,
                name=choiceName
            )


        self.repos.dishes.commit()

        return Result(self.parent.RESULT.SUCCESS, dishId)


    def get(self, dishId: int):
        '''获取菜品信息'''

        dish = self.repos.dishes.get(id=dishId)

        if not dish:
            return Result(self.parent.RESULT.DISH_NOT_FOUND)
        
        dishStats = self.repos.dishStats.get(id=dishId)
        dishChoices = self.repos.dishChoices.getAll(dishId=dishId)

        dish = dict(dish)

        dish["stats"] = dishStats
        dish["choices"] = dishChoices


        return Result(self.parent.RESULT.SUCCESS, dish)

    def delete(self, dishId: int):
        '''
        （软）删除菜品。
        '''
        
        code, data = self.get(dishId)

        if code != self.parent.RESULT.SUCCESS:
            return Result(code)

        data = cast(dict, data)

        deletedName = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + data["name"]


        try:
            self.repos.dishes.update(
                where={"id": dishId},
                data={"isDeleted": True, "name": deletedName}
            )

            self.repos.dishStats.delete(
                where={"id": dishId}
            )


            self.repos.dishChoices.delete(
                where={"dishId": dishId}
            )

            self.repos.dishes.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.DISH_NOT_FOUND)

        return Result(self.parent.RESULT.SUCCESS)

    def deleteByCategory(self, categoryId: int):
        '''
        删除一个分类下的所有菜品
        '''

        dishes = self.repos.dishes.getAll(category=categoryId, isDeleted=False)

        # if not dishes:
        #     return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        for dish in dishes:

            deletedName = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + dish["name"]

            self.repos.dishes.update(
                where={"id": dish["id"]},
                data={"isDeleted": True, "name": deletedName}
            )

            self.repos.dishStats.delete(
                where={"dishId": dish["id"]}
            )

            self.repos.dishChoices.delete(
                where={"dishId": dish["id"]}
            )

        self.repos.dishes.commit()

        return Result(self.parent.RESULT.SUCCESS)

    def _updateDishItems(self, dishId: int, changedItems: dict):
        '''
        [私有] 更新菜品基本信息
        '''

        columnsName = [col.name for col in self.repos.dishes.columns]

        for key in changedItems.keys():
            if key not in columnsName:
                return Result(self.parent.RESULT.CHANGED_ITEMS_NOT_FOUND, key)

        try:
            self.repos.dishes.update(
                where={"id": dishId},
                data=changedItems
            )

        except TypeMismatchError:
            return Result(self.parent.RESULT.VALUE_ERROR)
        except RecordNotFoundError:
            return Result(self.parent.RESULT.DISH_NOT_FOUND, dishId)

        self.repos.dishes.commit()

        return Result(self.parent.RESULT.SUCCESS)
    

    def _updateDishChoices(self, dishId: int, changedChoices: list[dict]):
        '''
        [私有] 更新菜品的选项信息
        '''
        PAIR = {
            "new_option": "delete_option",
            "delete_option": "new_option",
            "new_choice": "delete_choice",
            "delete_choice": "new_choice",
        }
    
        remain = {}

        for item in changedChoices:
            t = item["type"]

            if t in ("new_option", "delete_option"):
                key = ("option", item["name"], item["option"])
            else:
                key = ("choice", item["name"])

            if key not in remain:
                remain[key] = item
                continue

            prev = remain[key]

            if PAIR.get(prev["type"]) == t:
                # 配对成功，删除
                del remain[key]
            else:
                remain[key] = item

        uniqueChoices = list(remain.values())
        

        # 执行数据库命令，更新菜品选择
        for action in uniqueChoices:
            if action["type"] == "new_choice":
                # 新增选择
                # self.conn.execute(self.sql_parse.get("dishes.choices.new"),
                #                     (dish_id, action["name"], json.dumps([]), ))

                self.repos.dishChoices.insert(
                    dishId=dishId,
                    name=action["name"],
                    options=[]
                )

            
            elif action["type"] == "delete_choice":
                # 删除选择

                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.repos.dishChoices.update(
                    where={"dishId": dishId, "name": action["name"]},
                    data={"isDeleted": True, "name": f"{action["name"]}-{now}"}
                )
                
                
                # print("删除项目：", action["name"])

            
            elif action["type"] == "new_option" or action["type"] == "delete_option":
                
                # 获取选项
                # print(type(dish_id))
                # choices = self.conn.execute(self.sql_parse.get("dishes.choices.get_options"),
                #                             (dish_id, action["name"], )).fetchone()
                
                # if not choices:
                #     raise NotFoundError(str((dish_id, action["name"], )))
                
                # options = json.loads(choices["options"])

                # if action["type"] == "new_option":
                #     options.append(action["option"])
                # else:
                #     options.remove(action["option"])

                # self.conn.execute(self.sql_parse.get("dishes.choices.update"),
                #                     (json.dumps(options), dish_id, action["name"], ))

                # 获取选项
                choice = self.repos.dishChoices.get(dishId=dishId, name=action["name"])

                if not choice:
                    return Result(self.parent.RESULT.CHOICE_NOT_FOUND, action["name"])

                options = choice["options"]

                if action["type"] == "new_option":
                    options.append(action["option"])
                else:
                    options.remove(action["option"])

                self.repos.dishChoices.update(
                    where={"id": choice["id"]},
                    data={"options": options}
                )

        self.repos.dishChoices.commit()



        return Result(self.parent.RESULT.SUCCESS)

        
    def update(self, dishId: int, changedItems: dict, changedChoices: list):

        if changedItems:
            result = self._updateDishItems(dishId, changedItems)

            if result.code != self.parent.RESULT.SUCCESS:
                self.repos.dishes.rollback()

                return result
        

        if changedChoices:
            result = self._updateDishChoices(dishId, changedChoices)

            if result.code != self.parent.RESULT.SUCCESS:
                self.repos.dishChoices.rollback()

                return result

        return Result(self.parent.RESULT.SUCCESS)


class Tables:
    def __init__(self, repos: RepositoryManager, parent: ShopService):
        self.repos = repos
        self.parent = parent

    def getAll(self):
        result = self.repos.tables.getAll(isDeleted=False)

        return Result(self.parent.RESULT.SUCCESS, result)

    def create(self, name: str):
        try:
            tableId = self.repos.tables.insert(
                name=name,
                isAvailable=True,
                isDeleted=False
            )
        except UniqueConstraintError:
            return Result(self.parent.RESULT.TABLE_ALREADY_EXIST)

        self.repos.tables.commit()

        return Result(self.parent.RESULT.SUCCESS, tableId)

    def update(self, tableId: int, name: str):
        try:
            self.repos.tables.update(
                where={"id": tableId},
                data={"name": name}
            )
        except RecordNotFoundError:
            return Result(self.parent.RESULT.TABLE_NOT_FOUND, tableId)

        except UniqueConstraintError:
            return Result(self.parent.RESULT.TABLE_ALREADY_EXIST)

        self.repos.tables.commit()

        return Result(self.parent.RESULT.SUCCESS)

    def delete(self, tableId: int):

        tableInfo = self.repos.tables.get(id=tableId)

        if not tableInfo:
            return Result(self.parent.RESULT.TABLE_NOT_FOUND, tableId)
        
        now = datetime.datetime.now()

        deletedName = tableInfo["name"] + now.strftime("%Y-%m-%d %H:%M:%S")

        self.repos.tables.update(
            where={"id": tableId},
            data={"name": deletedName, "isDeleted": True}
        )

        return Result(self.parent.RESULT.SUCCESS)

    def get(self, tableId: int):
        tableInfo  =self.repos.tables.get(id=tableId)

        if not tableInfo:
            return Result(self.parent.RESULT.TABLE_NOT_FOUND, tableId)

        return Result(self.parent.RESULT.SUCCESS, tableInfo)
    

class ShopService(Service):
    RESULT = ResultCode

    def __init__(self, repositoryManager: RepositoryManager):
        super().__init__(repositoryManager)

        self.dishesCategory = DishCategory(repositoryManager, self)
        self.dishes = Dishes(repositoryManager, self)
        self.tables = Tables(repositoryManager, self)
        
