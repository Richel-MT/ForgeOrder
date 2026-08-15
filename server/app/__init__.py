from .views.accounts import accountsBlueprint
from .views.basic import basicBlueprint
from .views.shop import shopBlueprint
from .views.system import systemBlueprint

blueprints = [
    basicBlueprint,
    accountsBlueprint,
    shopBlueprint,
    systemBlueprint
]