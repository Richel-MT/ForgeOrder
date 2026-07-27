import sqlite3
import datetime
import json

from core.db.sql_parse import SqlParse
from core.db.exceptions import NotFoundError, ColumnNotFoundError
from .exceptions import CategoryNotFoundError

class DishesCategory:
    def __init__(self, conn: sqlite3.Connection, sql_parse: SqlParse):
        self.conn = conn
        self.sql_parse = sql_parse

        self.conn.executescript(self.sql_parse.get("dishes.create"))
        self.conn.commit()

    def get_all(self) -> list[sqlite3.Row]:
        '''
        获取所有分类。

        注意：数据库使用了RowFactory，返回一个Row对象列表。
        '''
        cursor = self.conn.execute(self.sql_parse.get("dishes.category.get_all"))
        return cursor.fetchall()
    
    def new(self, name: str) -> int:
        '''
        创建一个新分类。返回新分类的id

        注意：在分类存在时抛出ValueError。不抛出异常的方法为new_s。
        '''
        try:
            cursor = self.conn.execute(self.sql_parse.get("dishes.category.new"), (name,))
        except sqlite3.IntegrityError:
            raise ValueError(f"Category {name} already exists")
        
        else:
            self.conn.commit()
        
            return cursor.lastrowid # type: ignore
             
    def new_s(self, name: str) -> int:
        '''
        创建一个新分类。若分类已存在，则返回这个分类的id。

        注意：本方法不抛出异常（与new相对）
        '''

        # 检查分类是否存在

        category = self.get_from_name(name)
        if category:
            return category["id"]
        else:
            return self.new(name)
        
    
    def get_from_id(self, id: int) -> sqlite3.Row | None:
        '''
        根据id获取分类。

        注意：数据库使用了RowFactory，返回一个Row对象或None。
        '''
        result = self.conn.execute(self.sql_parse.get("dishes.category.get_from_id"), (id,)).fetchone()

        if result:
            return result
        else:
            raise NotFoundError(str(id))
    
    def get_from_name(self, name: str) -> sqlite3.Row | None:
        '''
        根据名称获取分类。

        注意：数据库使用了RowFactory，返回一个Row对象或None。
        '''
        cursor = self.conn.execute(self.sql_parse.get("dishes.category.get_from_name"), (name,))
        return cursor.fetchone()
    
    def update(self, id: int, name: str) -> None:
        '''
        更新分类名称。
        '''
        cursor = self.conn.execute(self.sql_parse.get("dishes.category.set_name"), (name, id))
        if cursor.rowcount == 0:
                    raise NotFoundError(str(id))
        self.conn.commit()
    
    def delete(self, id: int): 
        '''
        删除分类。

        '''

        cursor = self.conn.execute(self.sql_parse.get("dishes.category.delete"), (id,))

        if cursor.rowcount == 0:
            raise NotFoundError(str(id))
        
        self.conn.commit()

   
class Dishes:
    def __init__(self, parent_database, conn: sqlite3.Connection, sql_parse: SqlParse):
        self.conn = conn
        self.sql_parse = sql_parse
        self.parent_database = parent_database

    def create(self,
               name: str,
               price: int, # 单位：分
               category_id: int,
               description: str = "",
               image: str = "",
               is_available: bool = True,
               choices: dict = {}
               ):
        '''
        创建一个新菜品。
        '''

        # 生成创建时间
        created_at = datetime.datetime.now()
        
        # 验证分类是否存在
        category = self.parent_database.category.get_from_id(category_id)
        if not category:
            raise CategoryNotFoundError(category_id)
        
        category = dict(category)

        
        
        # 执行create1和create2命令以在dishes和dish_stats表中创建新菜品
        cursor = self.conn.execute(
            self.sql_parse.get("dishes.dishes.create"),
            (name, price, category_id, description, image, is_available, created_at)
            )
        
        dish_id = cursor.lastrowid

        cursor = self.conn.execute(
            self.sql_parse.get("dishes.stats.create"),
            (dish_id, created_at)
            )
        
        # 执行create3命令以在dish_choices表中创建新菜品的选择
        # 判断是否有选择
        if choices != {}:
            for name, options in choices.items():

                if not (isinstance(name, str) and isinstance(options, list)):
                    # 验证选择类型
                    raise ValueError(f"Choice type error: {name}")
                
                for option in options: #type: ignore
                    # 验证选项类型
                    if not isinstance(option, str):
                        raise ValueError(f"Option type error in {name}: {option}(type: {type(option).__name__}")
                    
                # 执行create3命令以在dish_choices表中创建新菜品的选择
                self.conn.execute(
                    self.sql_parse.get("dishes.choices.create"),
                    (dish_id, name, json.dumps(options))
                )
        
        # 提交事务
        self.conn.commit()

        return dish_id


    def get_all(self):
        '''
        获取所有菜品。
        '''
        # 准备返回结构
        result: dict[int, list] = {}

        # 1、获取所有分类并构建id->name映射，同时初始化每个分类的列表
        categories = self.parent_database.category.get_all()
        categories_map = {category["id"]: category["name"] for category in categories}
        for cid in categories_map.keys():
            result[cid] = []

        # 2、一次性获取所有相关表数据
        dishes_rows = self.conn.execute(self.sql_parse.get("dishes.get_all")).fetchall()
        dish_stats_rows = self.conn.execute(self.sql_parse.get("dishes.stats.get_all")).fetchall()
        dish_choices_rows = self.conn.execute(self.sql_parse.get("dishes.choices.get_all")).fetchall()

        # 3、构建索引以避免嵌套循环
        stats_map = {stat["id"]: dict(stat) for stat in dish_stats_rows}

        choices_map: dict[int, dict[str, list]] = {}
        for choice in dish_choices_rows:
            did = choice["dish_id"]
            if did not in choices_map:
                choices_map[did] = {}
            choices_map[did][choice["name"]] = json.loads(choice["options"])

        # 4、组装菜品并分配到分类中
        for row in dishes_rows:
            dish = dict(row)

            # 附加统计信息（如果存在）
            stat = stats_map.get(dish["id"])
            if stat is not None:
                dish["stat"] = stat

            # 附加选择（如果存在）
            ch = choices_map.get(dish["id"])
            if ch is not None:
                dish["choices"] = ch

            # 将菜品加入对应分类，若分类缺失则创建一个临时列表
            try:
                cid = int(dish["category"])
            except Exception:
                cid = None

            if cid is None or cid not in result:
                # 把未知分类也放入结果（使用id作为键）
                if cid is None:
                    continue
                result.setdefault(cid, []).append(dish)
            else:
                result[cid].append(dish)

        # 5、将result的key转换为分类名称并返回
        result_by_name: dict[str, list] = {}
        for cid, items in result.items():
            name = categories_map.get(cid, str(cid))
            result_by_name[name] = items

        return result_by_name, categories_map


    def get_from_id(self, dish_id: int):
        '''
        获取菜品信息。
        '''
        dish_data = self.conn.execute(self.sql_parse.get("dishes.get"), (dish_id,)).fetchone()

        if not dish_data:
            raise NotFoundError(str(dish_id))
        
        result = dict(dish_data)

        choices = self.conn.execute(self.sql_parse.get("dishes.choices.get"), (dish_id,)).fetchall()
        
        result["choices"] = {}
        for choice in choices:
            result["choices"][choice["name"]] = json.loads(choice["options"])
        
        return result

    def gets_from_category(self, category_id: int):
        '''
        获取分类下的所有菜品。
        '''
        result = self.conn.execute(self.sql_parse.get("dishes.get_from_category"), (category_id,)).fetchall()
               
        return [dict(dish) for dish in result]
    
    def _update_dishes(self, dish_id: int, changed_items):
        '''
        更新菜品信息。
        '''
        # 获取所有列
        
        columns = list(self.parent_database.get_all_columns("dishes"))

            
        for key in changed_items.keys():
            if key not in columns:
                raise ColumnNotFoundError("dishes", key)
        
        
        query_keys = ""
        for key, value in changed_items.items():
            query_keys += f"{key} = ?,"

        query_keys = query_keys.rstrip(",")

        # query_sql_values = ("VALUES (" + "?," * (len(changed_items.values()) + 1)).rstrip(",") + ")" 
        query_sql_values = ''
        

        
        cursor = self.conn.execute(
            self.sql_parse.get("dishes.update").format(settings = query_keys,
                                                       value = query_sql_values),
            list(changed_items.values()) + [dish_id])
        
        # 判断是否更新成功
        if cursor.rowcount == 0:
            raise NotFoundError(str(dish_id))
        
        # 提交事务
        self.conn.commit()

    def _update_dish_choices(self, dish_id: int, changed_choices: list[dict]):
        '''
        更新菜品选择。
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
                self.conn.execute(self.sql_parse.get("dishes.choices.new"),
                                  (dish_id, action["name"], json.dumps([]), ))
            
            elif action["type"] == "delete_choice":
                # 删除选择
                self.conn.execute(self.sql_parse.get("dishes.choices.delete"),
                                  (dish_id, action["name"], ))
                
                # print("删除项目：", action["name"])

            
            elif action["type"] == "new_option" or action["type"] == "delete_option":
                
                # 获取选项
                # print(type(dish_id))
                choices = self.conn.execute(self.sql_parse.get("dishes.choices.get_options"),
                                          (dish_id, action["name"], )).fetchone()
                
                if not choices:
                    raise NotFoundError(str((dish_id, action["name"], )))
                
                options = json.loads(choices["options"])

                if action["type"] == "new_option":
                    options.append(action["option"])
                else:
                    options.remove(action["option"])

                self.conn.execute(self.sql_parse.get("dishes.choices.update"),
                                  (json.dumps(options), dish_id, action["name"], ))
                
                # print("删除项目：", action["option"])
                
            
        self.conn.commit()
            


    def update(self, dish_id: int, changed_items: dict, changed_choices: list):
        if changed_items:
            self._update_dishes(dish_id, changed_items)
        
        if changed_choices:
            self._update_dish_choices(dish_id, changed_choices)
        
    
    def delete(self, dish_id: int):
        cursor = self.conn.execute(self.sql_parse.get("dishes.delete"),
                              (dish_id,))
            
        if cursor.rowcount == 0:
            raise NotFoundError(str(dish_id))
        
        self.conn.execute(self.sql_parse.get("dishes.choices.delete"),
                              (dish_id, ))
        
        self.conn.execute(self.sql_parse.get("dishes.stats.delete"),
                              (dish_id, ))

        self.conn.commit()

        return True 

    def delete_by_category(self, category_id: int):
        cursor = self.conn.execute(self.sql_parse.get("dishes.delete_by_category"),
                              (category_id,))
            
        self.conn.commit()

        return True 
 