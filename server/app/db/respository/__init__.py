from core.database.repository.manager import RepositoryManagerBase
from core.database.database import Database
from .dishes import *
from .orders import *
from .print_task import PrintTaskRepository
from .settings import SettingsRepository
from .tables import TablesRepository
from .users import UsersRepository
from .tokens import TokenRepository

class RepositoryManager(RepositoryManagerBase):

    def __init__(self, db: Database):
        super().__init__(db)

        self.users = UsersRepository(db)
        self.tokens = TokenRepository(db)
        

        self.tables = TablesRepository(db)
        self.settings = SettingsRepository(db)
        self.print_task = PrintTaskRepository(db)

        self.dishes_category = DishesCategoryRepository(db)
        self.dishes = DishesRepository(db)
        self.dish_stats = DishStatsRepository(db)
        self.dish_choices = DishChoicesRepository(db)

        self.orders = OrdersRepository(db)
        self.sub_orders = SubOrdersRepository(db)
        self.order_status = OrderStatusRepository(db)
        self.order_items = OrderItemsRepository(db)

    def init(self):
        self.users._init()
        self.tokens._init()
        self.tables._init()
        self.settings._init()
        self.print_task._init()
        self.dishes_category._init()
        self.dishes._init()
        self.dish_stats._init()
        self.dish_choices._init()
        self.orders._init()
        self.sub_orders._init()
        self.order_status._init()
        self.order_items._init()

        




