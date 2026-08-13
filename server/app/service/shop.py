import datetime
from enum import Enum, auto
from typing import cast

from .base import Service, Result
from app.db.respository import RepositoryManager
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


class DishCategory:

    def __init__(self, repos: RepositoryManager, parent: 'ShopService'):
        self.repos = repos
        self.parent = parent

    def get_all(self):
        '''
        获取所有菜品的分类。
        '''
        result = self.repos.dishesCategory.get_all(isDeleted=False)
        return Result(self.parent.RESULT.SUCCESS, result)

    def create(self, name: str):
        '''
        创建菜品分类。
        '''
        try:
            category_id = self.repos.dishesCategory.insert(name=name)
        except UniqueConstraintError:
            return Result(self.parent.RESULT.CATEGORY_ALREADY_EXIST)

        self.repos.dishesCategory.commit()

        return Result(self.parent.RESULT.SUCCESS, category_id)

    def update(self, category_id: int, name: str):
        '''
        更新菜品分类的名称。
        '''
        try:
            self.repos.dishesCategory.update(
                where={"id": category_id, "isDeleted": False},
                data={"name": name}
            )

            self.repos.dishesCategory.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        return Result(self.parent.RESULT.SUCCESS)

    def delete(self, category_id: int):
        '''
        （软）删除菜品分类。
        '''
        name = datetime.datetime.now().strftime("deleted_at_%Y%m%d%H%M%S")

        try:
            self.repos.dishesCategory.update(
                where={"id": category_id},
                data={"isDeleted": True, "name": name}
            )

            self.repos.dishesCategory.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        

        return Result(self.parent.RESULT.SUCCESS, name)

    def get(self, category_id: int):
        '''
        获取一个菜品分类。
        '''

        category = self.repos.dishesCategory.get(
                id=category_id, isDeleted=False
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

        dish_rows = self.repos.dishes.get_all(isDeleted=False)
        dish_stats_rows = self.repos.dishStats.get_all()
        dish_choices_rows = self.repos.dishChoices.get_all()

        # 处理返回值
        # 1、处理菜品分类信息，将其转换为{id:名称}的形式
        result_categories = {row["id"]: row["name"] for row in category_rows}

        # 2、初始化菜品结果的结构
        result_dishes = {row["name"]: [] for row in category_rows}

        # 3、构建菜品统计信息和菜品选项信息的索引以快速访问
        dish_stats_index = {row["id"]: row for row in dish_stats_rows}

        dish_choices_index = {}

        for choice in dish_choices_rows:
            dish_id = choice["dishId"]

            if dish_id not in dish_choices_index:
                dish_choices_index[dish_id] = {}

            dish_choices_index[dish_id][choice["name"]] = choice["options"]
        

        # 3、遍历菜品，将菜品信息组装到结果中
        for dish in dish_rows:

            # 获取菜品的分类名称
            category_id = dish["category"]
            category_name = result_categories[category_id]

            # 将菜品的统计信息添加到菜品信息中
            dish_ = dict(dish.copy())
            
            dish_["stats"] = dish_stats_index.get(dish_['id'], {})

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
            isAvailable=is_available,
            createdAt=create_time
        )

        self.repos.dishes.commit()

        return Result(self.parent.RESULT.SUCCESS, dish_id)


    def get(self, dish_id: int):
        '''获取菜品信息'''

        dish = self.repos.dishes.get(id=dish_id)

        if not dish:
            return Result(self.parent.RESULT.DISH_NOT_FOUND)
        
        dish_stats = self.repos.dishStats.get(id=dish_id)
        dish_choices = self.repos.dishChoices.get_all(dishId=dish_id)

        dish = dict(dish)

        dish["stats"] = dish_stats
        dish["choices"] = dish_choices


        return Result(self.parent.RESULT.SUCCESS, dish)

    def delete(self, dish_id: int):
        '''
        （软）删除菜品。
        '''
        
        code, data = self.get(dish_id)

        if code != self.parent.RESULT.SUCCESS:
            return Result(code)

        data = cast(dict, data)

        deleted_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + data["name"]


        try:
            self.repos.dishes.update(
                where={"id": dish_id},
                data={"is_deleted": True, "name": deleted_name}
            )

            self.repos.dishStats.delete(
                where={"dish_id": dish_id}
            )


            self.repos.dishChoices.delete(
                where={"dish_id": dish_id}
            )

            self.repos.dishes.commit()
        except RecordNotFoundError:
            return Result(self.parent.RESULT.DISH_NOT_FOUND)

        return Result(self.parent.RESULT.SUCCESS)

    def delete_by_category(self, category_id: int):
        '''
        删除一个分类下的所有菜品
        '''

        dishes = self.repos.dishes.get_all(category=category_id, isDeleted=False)

        # if not dishes:
        #     return Result(self.parent.RESULT.CATEGORY_NOT_FOUND)

        for dish in dishes:

            deleted_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + dish["name"]

            self.repos.dishes.update(
                where={"id": dish["id"]},
                data={"is_deleted": True, "name": deleted_name}
            )

            self.repos.dishStats.delete(
                where={"dish_id": dish["id"]}
            )

            self.repos.dishChoices.delete(
                where={"dish_id": dish["id"]}
            )

        self.repos.dishes.commit()

        return Result(self.parent.RESULT.SUCCESS)

    def _update_dish_items(self, dish_id: int, changed_items: dict):
        '''
        [私有] 更新菜品基本信息
        '''

        columns_name = [col.name for col in self.repos.dishes.columns]

        for key in changed_items.keys():
            if key not in columns_name:
                return Result(self.parent.RESULT.CHANGED_ITEMS_NOT_FOUND, key)

        try:
            self.repos.dishes.update(
                where={"id": dish_id},
                data=changed_items
            )

        except TypeMismatchError:
            return Result(self.parent.RESULT.VALUE_ERROR)
        except RecordNotFoundError:
            return Result(self.parent.RESULT.DISH_NOT_FOUND, dish_id)

        self.repos.dishes.commit()

        return Result(self.parent.RESULT.SUCCESS)
    

    def _update_dish_choices(self, dish_id: int, changed_choices: list[dict]):
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

        for item in changed_choices:
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

        unique_choices = list(remain.values())
        

        # 执行数据库命令，更新菜品选择
        for action in unique_choices:
            if action["type"] == "new_choice":
                # 新增选择
                # self.conn.execute(self.sql_parse.get("dishes.choices.new"),
                #                     (dish_id, action["name"], json.dumps([]), ))

                self.repos.dishChoices.insert(
                    dish_id=dish_id,
                    name=action["name"],
                    options=[]
                )

            
            elif action["type"] == "delete_choice":
                # 删除选择

                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.repos.dishChoices.update(
                    where={"dish_id": dish_id, "name": action["name"]},
                    data={"is_deleted": True, "name": f"{action["name"]}-{now}"}
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
                choice = self.repos.dishChoices.get(dish_id=dish_id, name=action["name"])

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

        
    def update(self, dish_id: int, changed_items: dict, changed_choices: list):

        if changed_items:
            result = self._update_dish_items(dish_id, changed_items)

            if result.code != self.parent.RESULT.SUCCESS:
                self.repos.dishChoices.rollback()

                return result
        

        if changed_choices:
            result = self._update_dish_choices(dish_id, changed_choices)

            if result.code != self.parent.RESULT.SUCCESS:
                self.repos.dishChoices.rollback()

                return result

        return Result(self.parent.RESULT.SUCCESS)



        



    



class ShopService(Service):
    RESULT = ResultCode

    def __init__(self, repo_manager: RepositoryManager):
        super().__init__(repo_manager)

        self.dishes_category = DishCategory(repo_manager, self)
        self.dishes = Dishes(repo_manager, self)
        
