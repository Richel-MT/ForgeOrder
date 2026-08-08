from flask import g

import extensions

from .respository import RepositoryManager
from core.database.database import Database


def get_database():
    if "database" not in g:
        g.database = get_database_()

    if "repos" not in g:
        g.repos = RepositoryManager(g.database)
        
    return g.repos


def close_database():
    if "repos" in g:
        g.repos = None
        
    if "database" in g:
        g.database.close()

def get_database_():
    db =  Database(extensions.config.get("database.path"))

    try:
        db._is_available()
    except:
        db.connect()

    return db
    