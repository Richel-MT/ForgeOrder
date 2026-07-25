from flask import g

import extensions

from .main_db import MainDatabase


def get_database_flask():
    if "database" not in g:
        g.database = MainDatabase(extensions.config.get("database.path"))
        
    return g.database



def close_database_flask():
    if "database" in g:
        g.database.close()

def get_database():
    return MainDatabase(extensions.config.get("database.path"))
    