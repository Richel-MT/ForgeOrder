from flask import g

import extensions

from .respository import RepositoryManager
from core.database.database import Database


def get_database():
    if "database" not in g:
        g.database = Database(extensions.config.get("database.path"))
        g.database.connect()

    if "repos" not in g:
        g.repos = RepositoryManager(g.database)
        
    return g.repos


def close_database():
    if "repos" in g:
        g.repos = None
        
    if "database" in g:
        g.database.close()

def get_database_():
    return Database(extensions.config.get("database.path"))
    