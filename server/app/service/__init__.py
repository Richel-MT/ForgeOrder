from dataclasses import dataclass
from typing import Any

from core.database.service import ServiceBase
from ..db.respository import RepositoryManager

class Service(ServiceBase):
    def __init__(self, repo_manager: RepositoryManager):
            self.repo_manager = repo_manager

@dataclass
class Result:
      code: Any
      data: Any | None = None
    