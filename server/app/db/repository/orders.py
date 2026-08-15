from typing import TypedDict
import datetime

from core.database.repository import Repository, Column
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class _OrdersRow(TypedDict):
    id: int
    type: int
    tableId: int
    partySize: int

class OrdersRepository(Repository[_OrdersRow]):
    tableName = "orders"

    columns = [
        Column("id", Integer(), primaryKey=True),
        Column("type", Integer(), notNull=True), #  0: 堂食 --1：打包
        Column("tableId", Integer(), notNull=True, foreign=("tables", "id")),
        Column("partySize", Integer(), notNull=True, default=1), # 人数，默认1人
    ]



class _SubOrdersRow(TypedDict):
    id: int
    note: str | None
    createdAt: datetime.datetime

class SubOrdersRepository(Repository[_SubOrdersRow]):
    tableName = "subOrders"

    columns = [
        Column("id", Integer(), primaryKey=True, foreign=("orders", "id")),
        Column("note", String()), # 子订单备注
        Column("createdAt", DateTime(), notNull=True), # 子订单的创建时间
    ]

class _OrderStatusRow(TypedDict):
    id: int
    status: int
    createdAt: datetime.datetime
    creator: int
    updatedAt: datetime.datetime
    finishedAt: datetime.datetime | None
    payAt: datetime.datetime | None
    cashier: int
    payMethod: int | None
    totalAmount: int
    discount: int | None
    discountType: int | None

class OrderStatusRepository(Repository[_OrderStatusRow]):
    tableName = "orderStatus"

    columns = [
        Column("id", Integer(), primaryKey=True, foreign=("orders", "id")),
        Column("status", Integer(), notNull=True), # 0: 已下单 --1: 制作中 --2: 待结账 --3: 已结账
        Column("createdAt", DateTime(), notNull=True), # 下单时间

        Column("creator", Integer(), notNull=True, foreign=("users", "id")),  # 创建人id
        Column("updatedAt", DateTime(), notNull=True), # 最后更新时间
        Column("finishedAt", DateTime()), # 完成时间（菜品全部完成）
        Column("payAt", DateTime()), # 支付时间
        Column("cashier", Integer(), notNull=True, foreign=("users", "id")),  # 收银员id
        Column("payMethod", Integer()), # 0: 现金 --1: 支付宝 --2: 微信
        Column("totalAmount", Integer(), notNull=True), # 订单总金额
        Column("discount", Integer()), # 优惠金额
        Column("discountType", Integer()), # 0: 抹零 --1: 优惠固定金额 --2: 按比例优惠
    ]

class _OrderItemsRow(TypedDict):
    id: int
    orderId: int
    subOrderId: int
    dishId: int
    price: int
    quantity: int
    totalPrice: int
    choices: dict | None
    isFinished: bool
    finishedAt: datetime.datetime | None

class OrderItemsRepository(Repository[_OrderItemsRow]):
    tableName = "orderItems"

    columns = [
        Column("id", Integer(), primaryKey=True, autoIncrement=True),

        Column("orderId", Integer(), notNull=True, foreign=("orders", "id")),
        Column("subOrderId", Integer(), notNull=True, foreign=("subOrders", "id")),  # 子订单id

        Column("dishId", Integer(), notNull=True, foreign=("dishes", "id")),  # 菜品id

        Column("price", Integer(), notNull=True),  # 单价
        Column("quantity", Integer(), notNull=True),  # 数量

        Column("totalPrice", Integer(), notNull=True),  # 总金额

        Column("choices", JSON()),  # 选择的选项

        Column("isFinished", Boolean(), notNull=True, default=False),  # 是否完成
        
        Column("finishedAt", DateTime()),  # 完成时间
    ]