from flask import g

import extensions

from .respository import RepositoryManager
from core.database.database import Database


def getDatabase():
    '''
    获取一个数据库连接，如果不存在则创建。
    注意：需在请求上下文中调用。
    '''
    if "database" not in g:
        g.database = getDatabase_()

    if "repos" not in g:
        g.repos = RepositoryManager(g.database)
        
    return g.repos


def closeDatabase():
    '''
    关闭数据库连接
    '''
    if "repos" in g:
        g.repos = None
        
    if "database" in g:
        g.database.close()

def getDatabase_():
    '''
    获取一个数据库连接，返回数据库连接对象。
    与`get_database`方法不同的是，此方法不一定需要请求上下文。
    '''
    db =  Database(extensions.config.get("database.path"))

    try:
        db._isAvailable()
    except:
        db.connect()

    return db
    