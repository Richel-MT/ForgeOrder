from typing import Any
from dataclasses import dataclass

from core.database.service import ServiceBase
from ..db.respository import RepositoryManager

class Service(ServiceBase):
    def __init__(self, repositoryManager: RepositoryManager):
            self.repositoryManager = repositoryManager

@dataclass
class Result:
    code: Any
    data: Any | None = None


    def __iter__(self):
        return iter((self.code, self.data))
