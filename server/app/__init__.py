from .views.accounts import accounts_bp
from .views.basic import basic_bp
from .views.shop import shop_bp
from .views.system import system_bp

blueprints = [
    basic_bp,
    accounts_bp,
    shop_bp,
    system_bp
]