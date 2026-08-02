from ..repository.manager import RepositoryManagerBase

class ServiceBase:
    def __init__(self, repo_manager: RepositoryManagerBase):
        self.repo_manager = repo_manager

