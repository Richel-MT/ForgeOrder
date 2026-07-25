from app.app_settings.manager import SettingsManager
from app.db.main_db import MainDatabase

class SettingsConnection:
    def __init__(self, db_name: str):
        self.db = MainDatabase(db_name)

        self.manager = SettingsManager(self.db)

        self.manager._init()


    def get(self, key):
        return self.manager.get(key)

    