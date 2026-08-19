from typing import TypedDict, cast 
import datetime

from core.database.repository import Repository, Column, RowType
from core.database.repository.schema import Integer, String, JSON, DateTime, Boolean

class _OrdersRow(TypedDict):
    id: str
    type: int
    tableId: int
    partySize: int

class _SubOrdersRow(TypedDict):
    id: int
    totalOrderId : str
    subOrderId: int
    note: str | None
    createdAt: datetime.datetime
    finishedAt: datetime.datetime | None

class _OrderStatusRow(TypedDict):
    id: str
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

class _OrderItemsRow(TypedDict):
    id: int
    orderId: str
    subOrderId: int
    dishId: int
    price: int
    quantity: int
    totalPrice: int
    choices: dict | None
    isFinished: bool
    finishedAt: datetime.datetime | None

class OrdersRepository(Repository[_OrdersRow]):
    tableName = "orders"

    columns = [
        Column("id", String(36), primaryKey=True), # uuid v7
        Column("type", Integer(), notNull=True), #  0: 堂食 --1：打包
        Column("tableId", Integer(), foreign=("tables", "id")),
        Column("partySize", Integer(), notNull=True, default=1), # 人数，默认1人 
    ]


class SubOrdersRepository(Repository[_SubOrdersRow]):
    tableName = "subOrders"

    columns = [
        Column("id", Integer(), primaryKey=True, autoIncrement=True),
        Column("totalOrderId", String(36), notNull=True, foreign=("orders", "id")),
        Column("subOrderId", Integer(), notNull=True),
        Column("note", String()), # 子订单备注
        Column("createdAt", DateTime(), notNull=True), # 子订单的创建时间
        Column("finishedAt", DateTime()), # 完成时间（菜品全部完成）
    ]

class OrderStatusRepository(Repository[_OrderStatusRow]):
    tableName = "orderStatus"

    columns = [
        Column("id", String(36), primaryKey=True, foreign=("orders", "id")),
        Column("status", Integer(), notNull=True), # 0: 已下单 --1: 制作中 --2: 待结账 --3: 已结账
        Column("createdAt", DateTime(), notNull=True), # 下单时间

        Column("creator", Integer(), notNull=True, foreign=("users", "id")),  # 创建人id
        Column("updatedAt", DateTime(), notNull=True), # 最后更新时间
        Column("finishedAt", DateTime()), # 完成时间（菜品全部完成）
        Column("payAt", DateTime()), # 支付时间
        Column("cashier", Integer(), foreign=("users", "id")),  # 收银员id

        Column("payMethod", Integer()), # 0: 现金 --1: 支付宝 --2: 微信
        Column("totalAmount", Integer(), notNull=True), # 订单总金额
        Column("discount", Integer()), # 优惠金额
        Column("discountType", Integer()), # 0: 抹零 --1: 优惠固定金额 --2: 按比例优惠
    ]

    def getTodayOrders(self, offset: int, limit: int):
        todayStart = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        todayEnd = todayStart + datetime.timedelta(days=1)

        stampTodayStart = self._convertTo(createdAt=todayStart)["createdAt"]
        stampTodayEnd = self._convertTo(createdAt=todayEnd)["createdAt"]

        cursor = self.execute(f'''SELECT * FROM {self.tableName} 
        WHERE createdAt >= ? AND createdAt <= ? 
        ORDER BY createdAt DESC
        LIMIT ? OFFSET ?
        ''',
                              (stampTodayStart, stampTodayEnd, limit, offset))

        result = cursor.fetchall()

        return cast(list[RowType], [self._convertFrom(**row) for row in result])




class OrderItemsRepository(Repository[_OrderItemsRow]):
    tableName = "orderItems"

    columns = [
        Column("id", Integer(), primaryKey=True, autoIncrement=True),

        Column("orderId", String(36), notNull=True, foreign=("orders", "id")),
        Column("subOrderId", Integer(), notNull=True, foreign=("subOrders", "id")),  # 子订单id

        Column("dishId", Integer(), notNull=True, foreign=("dishes", "id")),  # 菜品id

        Column("price", Integer(), notNull=True),  # 单价
        Column("quantity", Integer(), notNull=True),  # 数量

        Column("totalPrice", Integer(), notNull=True),  # 总金额

        Column("choices", JSON()),  # 选择的选项
        
        Column("finishedAt", DateTime()),  # 完成时间
    ]