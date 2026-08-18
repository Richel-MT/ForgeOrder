from .views.accounts import accountsBlueprint
from .views.basic import basicBlueprint
from .views.shop import shopBlueprint
from .views.system import systemBlueprint
from .views.orders import ordersBlueprint

blueprints = [
    accountsBlueprint,
    shopBlueprint,
    systemBlueprint,
    ordersBlueprint,
    basicBlueprint,
]