from ..database import Database

class RepositoryManager:
    '''数据库管理器'''
    def __init__(self, db: Database):
        self.db = db

