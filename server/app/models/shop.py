import time

from flask import g, request

from app.app_settings.manager import SettingsManager
from core.db.exceptions import ColumnNotFoundError, NotFoundError
from core.utils import make_response
from app.routes.app_bp import AppBlueprint
from app.db.main_db.exceptions import CategoryNotFoundError
from ..db.get_db import get_database_flask
from app.routes.field import *

shop_bp = AppBlueprint("shop", __name__)

# 店铺状态
@shop_bp.get("/api/shop/getBusinessState" , auth=True)
def get_business_state():
    db = get_database_flask()
    sm = SettingsManager(db)

    is_business = sm.get("shop.isBusiness")
    
    return make_response(
        0,
        is_business
    )

@shop_bp.post("/api/shop/setBusinessState",
            auth=True,
            is_admin=True,
            arguments=[
                RequestField("is_business", bool, True)
            ])
def set_business_state():
    is_business = g.args["is_business"]
    
    db = get_database_flask()
    sm = SettingsManager(db)

    sm.set("shop.isBusiness", is_business)

    g.logger.set_category("SHOP")
    g.logger.info({
        "is_business": is_business,
        "operator": g.user_info["user"]["id"]
    },  "UpdateBusinessState")

    return make_response(
        0,
        None
    )



# 菜品
@shop_bp.get("/api/shop/dishes/getAll" , auth=True)
def get_all_dishes():
    meta_db = get_database_flask()

    dishes, categories = meta_db.dishes.get_all()

    return make_response(
        0,
        {
            "dishes": dishes,
            "categories": categories
        }
    )

@shop_bp.post("/api/shop/dishes/get" , auth=True,
              arguments=[
                  RequestField("id", int, True)
              ])
def get_dish():
    dish_id = g.args["id"]


    meta_db = get_database_flask()

    try:
        dish = meta_db.dishes.get_from_id(dish_id)

    except NotFoundError as e:
        return make_response(
            3001,
            None
        ), 404


    return make_response(
        0,
        dict(dish)
    )

@shop_bp.post("/api/shop/dishes/update", auth=True, is_admin=True,
              arguments=[
                  RequestField("dish_id", int, True),
                  RequestField("changed_items", dict, True),
                  RequestField("changed_choices", list, True)
              ])
def update_dish():
    dish_id: int = g.args["dish_id"]
    changed_items : dict = g.args["changed_items"]
    changed_choices : list = g.args["changed_choices"]

    meta_db = get_database_flask()

    
    if AllOf( # failed
        Not(NotEmpty().bind(changed_items)), # null -> pass
        Not(NotEmpty().bind(changed_choices))  # null -> pass
    ).validate():
        
        return make_response(
            3001,
            None
        ), 400 

    g.logger.set_category("SHOP")
    


    try:
        meta_db.dishes.update(dish_id, changed_items, changed_choices)

        g.logger.info({
            "id": dish_id,
            "changed_items": changed_items,
            "changed_choices": changed_choices
        }, "UpdateDish")
        
        return make_response(
            0,
            None
        ), 200

    except ColumnNotFoundError as e:
        return make_response(
            3999,
            [e.table, e.name]
        ), 404
    
    except NotFoundError:
        return make_response(
            3002,
            None
        ), 404

@shop_bp.post("/api/shop/dishes/delete", auth=True, is_admin=True,
               arguments=[
                   RequestField("dish_id", int, True)
               ])
def delete_dish():
    dish_id: int = g.args["dish_id"]

    meta_db = get_database_flask()

    g.logger.set_category("SHOP")
    
    
    try:
        meta_db.dishes.delete(dish_id)

        g.logger.info({
                "id": dish_id
            }, "DeleteDish")

        
        return make_response(
            0,
            None
        ), 200
    except NotFoundError:
        return make_response(
            3001,
            None
        ), 404
    
@shop_bp.post("/api/shop/dishes/new", auth=True, is_admin=True, arguments=[
    RequestField("name", str, True, None, NotEmpty()),
    RequestField("price", int, True, None, Interval(Open(0), None)),
    RequestField("category", int, True),
    RequestField("description", str, False, ""),
    RequestField("image", str, False, ""),
    RequestField("is_available", bool, True),
    RequestField("choices", dict, False, {})
])
def new_dish():
    name: str = g.args["name"]
    price: int = g.args["price"]
    category: int = g.args["category"]
    description: str = g.args["description"]
    image: str = g.args["image"]
    is_available: bool = g.args["is_available"]
    choices: dict = g.args["choices"]

    meta_db = get_database_flask()

    g.logger.set_category("SHOP")

    try:
        dish_id = meta_db.dishes.create(
            name,
            price,
            category,
            description,
            image,
            is_available,
            choices
        )

        g.logger.info({
            "id": dish_id,
            "name": name,
            "price": price,
            "category": category,
            "description": description,
            "image": image,
            "is_available": is_available,
            "choices": choices
        }, "NewDish")

        return make_response(
            0,
            dish_id
        ), 200 # 创建成功
    
    except CategoryNotFoundError as e:
        return make_response(
            3001,
            e.category_id
        ), 404 # 找不到分类（3001）
    

# 分类
@shop_bp.post("/api/shop/category/delete", auth=True, is_admin=True,
              arguments=[
                  RequestField("cateogry_id", int, True)

              ])
def delete_category():
    category_id: int = g.args["category_id"]

    meta_db = get_database_flask()

    # 删除该分类下的所有菜品
    meta_db.dishes.delete_by_category(category_id)

    g.logger.set_category("SHOP")

    try:
        
        name = meta_db.category.get_from_id(category_id)["name"]

        meta_db.category.set_name(category_id, f"{name}_disabled_{time.time()}")

        meta_db.category.delete(category_id)

        g.logger.info({
                "id": category_id
            }, "DeleteCategory")
        
        return make_response(
            0,
            None
        ), 200
    
    except NotFoundError as e :
        # import traceback
        # traceback.print_exc()
        return make_response(
            3001,
            None
        ), 404

@shop_bp.get("/api/shop/category/getAll" , auth=True)
def get_all_categories():
    meta_db = get_database_flask()

    categories = meta_db.category.get_all()
    categories = [dict(category) for category in categories]

    return make_response(
        0,
        categories
    )


@shop_bp.post("/api/shop/category/update", auth=True, is_admin=True, 
              arguments=[
                  RequestField("category_id", int, True),
                  RequestField("category_name", str, True, None, NotEmpty())
              ])
def edit_category():


    category_id: int = g.args["category_id"]
    category_name: str = g.args["category_name"]

    meta_db = get_database_flask()

    g.logger.set_category("SHOP")

    try:
        meta_db.category.set_name(category_id, category_name)

        g.logger.info({
                "id": category_id,
                "name": category_name
            }, "UpdateCategory")

        return make_response(
            0,
            None
        ), 200
    except NotFoundError:
        return make_response(
            3001,
            None
        ), 404

@shop_bp.post("/api/shop/category/new", auth=True, is_admin=True,
              arguments=[
                  RequestField("name", str, True, None, NotEmpty())
              ])
def new_category():
    
    name: str = g.args["name"]

    meta_db = get_database_flask()

    g.logger.set_category("SHOP")

    try:
        category_id = meta_db.category.new(name)

        g.logger.info({
                "id": category_id,
                "name": name
            }, "NewCategory")
        
        return make_response(
                0,
                category_id
            ), 200
    except ValueError:
        return make_response(
            3001, 
            None
        ), 400 # 分类名称已存在（3001）
     

