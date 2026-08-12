import time
from typing import cast

from flask import g

from app.routes.res_generator import ResponseInfo
from app.service import SettingsService, ShopService
from core.utils import make_response
from app.routes.app_bp import AppBlueprint
from app.routes.field import *

shop_bp = AppBlueprint("shop", __name__)

# 店铺状态
@shop_bp.get("/api/shop/getBusinessState" , auth=True, 
             responses=[
                 ResponseInfo(0, "OK", bool)
             ])
def get_business_state():

    service = SettingsService(g.repos)

    is_business = service.get("shop.isBusiness")
    
    return g.res.OK(
        is_business
    )

@shop_bp.post("/api/shop/setBusinessState",
            auth=True,
            is_admin=True,
            arguments=[
                RequestField("is_business", bool, True)
            ],
            responses=[
                ResponseInfo(0, "OK", None)
            ])
def set_business_state():
    is_business = g.args["is_business"]
    
    service = SettingsService(g.repos)

    service.set("shop.isBusiness", is_business)

    g.logger.set_category("SHOP")

    g.logger.info({
        "is_business": is_business,
        "operator": g.user_info["user"]["id"]
    },  "UpdateBusinessState")

    return g.res.OK()



# 菜品
@shop_bp.get("/api/shop/dishes/getAll" , auth=True,
             responses=[
                 ResponseInfo(0, "OK", dict)
             ])
def get_all_dishes():

    service = ShopService(g.repos)

    _, data = service.dishes.get_all_v1()

    categories, dishes = cast(tuple, data)

    return g.res.OK(
        {
            "dishes": dishes,
            "categories": categories
        }
    )

@shop_bp.post("/api/shop/dishes/get" , auth=True,
              arguments=[
                  RequestField("id", int, True)
              ],
              responses=[
                  ResponseInfo(0, "OK", dict),
                  ResponseInfo(3001, "DishNotFound", None)
              ])
def get_dish():
    dish_id = g.args["id"]


    service = ShopService(g.repos)


    status, data = service.dishes.get(dish_id)

    if status == service.RESULT.DISH_NOT_FOUND:
        return g.res.DishNotFound()

    

    return g.res.OK(data)

@shop_bp.post("/api/shop/dishes/update", auth=True, is_admin=True,
              arguments=[
                  RequestField("dish_id", int, True),
                  RequestField("changed_items", dict, True),
                  RequestField("changed_choices", list, True)
              ],
              responses=[
                  ResponseInfo(0, "OK", None),
                  ResponseInfo(3001, "NoChange", None),
                  ResponseInfo(3002, "DishNotFound", None),
                  ResponseInfo(3003, "ChangedItemsNotFound", None), # 更改的信息不存在
                  ResponseInfo(3004, "ChangedItemsValueError", None), # 更改的信息 值非法
                  ResponseInfo(3005, "ChoiceNotFound", None) # 更改的选项不存在
              ])
def update_dish():
    dish_id: int = g.args["dish_id"]
    changed_items : dict = g.args["changed_items"]
    changed_choices : list = g.args["changed_choices"]

    service = ShopService(g.repos)

    
    if AllOf( # failed
        Not(NotEmpty().bind(changed_items)), # null -> pass
        Not(NotEmpty().bind(changed_choices))  # null -> pass
    ).validate():
        
        return g.res.NoChange()

    g.logger.set_category("SHOP")
    


    status, data = service.dishes.update(dish_id, changed_items, changed_choices)

    match status:
        case service.RESULT.SUCCESS:

            g.logger.info({
                "id": dish_id,
                "changed_items": changed_items,
                "changed_choices": changed_choices
            }, "UpdateDish")
            
            return g.res.OK()

        case service.RESULT.CHANGED_ITEMS_NOT_FOUND:
            return g.res.ChangedItemsNotFound({
                "id": dish_id,
                "key": data
            })

        case service.RESULT.DISH_NOT_FOUND:
            return g.res.DishNotFound({
                "id": dish_id
            })

        case service.RESULT.VALUE_ERROR:
            return g.res.ChangedItemsValueError({
                "id": dish_id,
            })

        case service.RESULT.CHOICE_NOT_FOUND:
            return g.res.ChoiceNotFound({
                "id": dish_id,
                "name": data
            })




@shop_bp.post("/api/shop/dishes/delete", auth=True, is_admin=True,
               arguments=[
                   RequestField("dish_id", int, True)
               ],
               responses=[
                   ResponseInfo(0, "OK", None),
                   ResponseInfo(3001, "DishNotFound", None)
               ])
def delete_dish():
    dish_id: int = g.args["dish_id"]

    service = ShopService(g.repos)

    g.logger.set_category("SHOP")
    
    
    status, data = service.dishes.delete(dish_id)

    if status == service.RESULT.DISH_NOT_FOUND:
        return g.res.DishNotFound()

    return g.res.OK()
    
@shop_bp.post("/api/shop/dishes/new", auth=True, is_admin=True, arguments=[
    RequestField("name", str, True, None, NotEmpty()),
    RequestField("price", int, True, None, Interval(Open(0), None)),
    RequestField("category", int, True),
    RequestField("description", str, False, ""),
    RequestField("image", str, False, ""),
    RequestField("is_available", bool, True),
    RequestField("choices", dict, False, {})
],
responses=[
    ResponseInfo(0, "OK", None),
    ResponseInfo(3001, "CategoryNotFound", None)
]
)
def new_dish():
    name: str = g.args["name"]
    price: int = g.args["price"]
    category: int = g.args["category"]
    description: str = g.args["description"]
    image: str = g.args["image"]
    is_available: bool = g.args["is_available"]
    choices: dict = g.args["choices"]

    service = ShopService(g.repos)

    g.logger.set_category("SHOP")

    status, data = service.dishes.create(name, price, category, description, is_available, choices)

    if status == service.RESULT.CATEGORY_NOT_FOUND:
        return g.res.CategoryNotFound()

    return g.res.OK()
    
    

# 分类
@shop_bp.post("/api/shop/category/delete", auth=True, is_admin=True,
              arguments=[
                  RequestField("cateogry_id", int, True)
              ],
              responses=[
                  ResponseInfo(0, "OK", None),
                  ResponseInfo(3001, "CategoryNotFound", None)
              ])
def delete_category():
    category_id: int = g.args["category_id"]


    g.logger.set_category("SHOP")

    service = ShopService(g.repos)

    status, data = service.dishes.delete_by_category(category_id)

    if status == service.RESULT.CATEGORY_NOT_FOUND:
        return g.res.CategoryNotFound()

    service.dishes_category.delete(category_id)
    
    return g.res.OK()

@shop_bp.get("/api/shop/category/getAll" , auth=True, 
             responses=[
                 ResponseInfo(0, "OK", None)
             ])
def get_all_categories():

    service = ShopService(g.repos)

    return g.res.OK(
        service.dishes_category.get_all().data
    )


@shop_bp.post("/api/shop/category/update", auth=True, is_admin=True, 
              arguments=[
                  RequestField("category_id", int, True),
                  RequestField("category_name", str, True, None, NotEmpty())
              ],
              responses=[
                  ResponseInfo(0, "OK", None),
                  ResponseInfo(3001, "CategoryNotFound", None)
              ])
def edit_category():
    category_id: int = g.args["category_id"]
    category_name: str = g.args["category_name"]

    service = ShopService(g.repos)

    g.logger.set_category("SHOP")

    status = service.dishes_category.update(category_id, category_name)

    if status == service.RESULT.CATEGORY_NOT_FOUND:
        return g.res.CategoryNotFound()

    return g.res.OK()

@shop_bp.post("/api/shop/category/new", auth=True, is_admin=True,
              arguments=[
                  RequestField("name", str, True, None, NotEmpty())
              ],
              responses=[
                  ResponseInfo(0, "OK", None),
                  ResponseInfo(3001, "CategoryNameExist", None)
              ])
def new_category():
    
    name: str = g.args["name"]


    g.logger.set_category("SHOP")


    service = ShopService(g.repos)
    status, data = service.dishes_category.create(name)

    if status == service.RESULT.CATEGORY_ALREADY_EXIST:
        return g.res.CategoryNameExist()
    
    return g.res.OK()
     
# 桌台
@shop_bp.get("/api/shop/tables/getAll", auth=True, responses=[
                  ResponseInfo(0, "OK", None)
              ])
def get_all_tables():
    db = get_database()

    tables = db.tables.get_all()

    return g.res.OK(
        tables
    )

@shop_bp.post("/api/shop/tables/new", auth=True, is_admin=True,
             arguments=[
                  RequestField("name", str, True, None, NotEmpty())
             ],
             responses=[
                  ResponseInfo(0, "OK", None),
                  ResponseInfo(3001, "TableNameExist", None)
             ])
def new_table():
    name: str = g.args["name"]

    db = get_database()

    g.logger.set_category("SHOP")

    try:
        table_id = db.tables.new(name, True)
    except ValueError:

        return g.res.TableNameExist()
    else:
        g.logger.info({
                "id": table_id,
                "name": name
            }, "NewTable")
        
        return g.res.OK()

@shop_bp.post("/api/shop/tables/update", auth=True, is_admin=True,
             arguments=[
                  RequestField("id", int, True),
                  RequestField("name", str, True, None, NotEmpty())
             ],
             responses=[
                  ResponseInfo(0, "OK", None),
                  ResponseInfo(3001, "TableNotFound", None),
                  ResponseInfo(3002, "TableNameExist", None)
             ])
def update_table():
    table_id: int = g.args["id"]
    new_name: str = g.args["name"]

    db = get_database()

    g.logger.set_category("SHOP")

    try:
        db.tables.update(table_id, new_name, True)
    except NotFoundError:
        return g.res.TableNotFound()

    except ValueError:
        return g.res.TableNameExist()
    
    else:
        g.logger.info({
                "id": table_id,
                "name": new_name
            }, "UpdateTable")
        
        return g.res.OK()

@shop_bp.post("/api/shop/tables/delete", auth=True, is_admin=True,
             arguments=[
                  RequestField("id", int, True)
             ],
             responses=[
                  ResponseInfo(0, "OK", None),
                  ResponseInfo(3001, "TableNotFound", None)
             ])
def delete_table():
    table_id: int = g.args["id"]


    db = get_database()
    g.logger.set_category("SHOP")

    try:
        db.tables.soft_delete(table_id)

    except NotFoundError:
        return g.res.TableNotFound()
    else:
        g.logger.info({
                "id": table_id
            }, "DeleteTable")
        
        return g.res.OK()




