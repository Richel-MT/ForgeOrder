from .settings import SettingsService
from .users import UserService
from .shop import ShopService
from .base import Service

from core.database.database import Database
from ..db.respository import RepositoryManager



def initService(databaseName: str, service: type[Service]):
    '''
    初始化一个Service对象。

    调用本函数时，将会创建一个数据库连接，初始化一个RepositoryManager对象以便快速使用Service。

    调用时，传入数据库连接名称和Service类，返回数据库连接、RepositoryManager对象和Service对象组成的元组。
    '''

    # 初始化数据库
    db = Database(databaseName)
    db.connect()

    # 初始化RepositoryManager
    repos = RepositoryManager(db)

    # 初始化Service
    service_ = service(repos)

    return db, repos, service_




    
    