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

        self.dishesCategory = DishesCategoryRepository(db)
        self.dishes = DishesRepository(db)
        self.dishStats = DishStatsRepository(db)
        self.dishChoices = DishChoicesRepository(db)

        self.orders = OrdersRepository(db)
        self.subOrders = SubOrdersRepository(db)
        self.orderStatus = OrderStatusRepository(db)
        self.orderItems = OrderItemsRepository(db)

    def init(self):
        self.users._init()
        self.tokens._init()
        self.tables._init()
        self.settings._init()
        self.print_task._init()
        self.dishesCategory._init()
        self.dishes._init()
        self.dishStats._init()
        self.dishChoices._init()
        self.orders._init()
        self.subOrders._init()
        self.orderStatus._init()
        self.orderItems._init()

        




