from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class OrdersRepository(Repository):
    table_name = "orders"

    columns = [
        Column("id", Integer(), primary_key=True),
        Column("type", Integer(), not_null=True), #  0: 堂食 --1：打包
        Column("table_id", Integer(), not_null=True, foreign=("tables", "id")),
        Column("party_size", Integer(), not_null=True, default=1), # 人数，默认1人
    ]



class SubOrdersRepository(Repository):
    table_name = "sub_orders"

    columns = [
        Column("id", Integer(), primary_key=True, foreign=("orders", "id")),
        Column("note", String()), # 子订单备注
        Column("created_at", DateTime(), not_null=True), # 子订单的创建时间
    ]

class OrderStatusRepository(Repository):
    table_name = "order_status"

    columns = [
        Column("id", Integer(), primary_key=True, foreign=("orders", "id")),
        Column("status", Integer(), not_null=True), # 0: 已下单 --1: 制作中 --2: 待结账 --3: 已结账
        Column("created_at", DateTime(), not_null=True), # 下单时间

        Column("creator", Integer(), not_null=True, foreign=("users", "id")),  # 创建人id
        Column("updated_at", DateTime(), not_null=True), # 最后更新时间
        Column("finished_at", DateTime()), # 完成时间（菜品全部完成）
        Column("pay_at", DateTime()), # 支付时间
        Column("cashier", Integer(), not_null=True, foreign=("users", "id")),  # 收银员id
        Column("pay_method", Integer()), # 0: 现金 --1: 支付宝 --2: 微信
        Column("total_amount", Integer(), not_null=True), # 订单总金额
        Column("discount", Integer()), # 优惠金额
        Column("discount_type", Integer()), # 0: 抹零 --1: 优惠固定金额 --2: 按比例优惠
    ]

class OrderItemsRepository(Repository):
    table_name = "order_items"

    columns = [
        Column("id", Integer(), primary_key=True, auto_increment=True),

        Column("order_id", Integer(), not_null=True, foreign=("dishes", "id")),  # 菜品id
        Column("sub_order_id", Integer(), not_null=True, foreign=("sub_orders", "id")),  # 子订单id

        Column("dish_id", Integer(), not_null=True, foreign=("dishes", "id")),  # 菜品id

        Column("price", Integer(), not_null=True),  # 单价
        Column("quantity", Integer(), not_null=True),  # 数量

        Column("total_price", Integer(), not_null=True),  # 总金额

        Column("choices", JSON()),  # 选择的选项

        Column("is_finished", Boolean(), not_null=True, default=False),  # 是否完成
        
        Column("finish_at", DateTime()),  # 完成时间
    ]
    
