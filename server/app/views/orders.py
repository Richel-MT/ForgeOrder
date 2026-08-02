from app.routes.app_bp import AppBlueprint
from app.routes.field import RequestField, NotEmpty, Choices, Interval, Open

orders_bp = AppBlueprint("orders", __name__)

@orders_bp.post("/api/order/new", auth=True, is_admin=True,
                arguments=[
                    RequestField("order_type", int, True, None, Choices(0, 1)),
                    RequestField("party_size", int, True, None, Interval(Open(0), None)),
                    RequestField("table_id", int, True, None, NotEmpty()),
                    RequestField("table_name", str, True, None, NotEmpty()),
                    RequestField("dishes", list, True, None, NotEmpty()),
                    RequestField("note", str, False, "")
                ])
def new_order():
    pass